import { EmailMessage } from "cloudflare:email";

/**
 * Email Relay Worker
 * 
 * Receives forwarded emails from Cloudflare Email Routing,
 * saves them as structured JSON + raw .eml to R2 storage.
 * 
 * Hermes (on the server) polls R2 periodically to pick up new emails.
 * 
 * Deployment: wrangler deploy
 */

// Acceptable senders — only process emails from known addresses
const ALLOWED_SENDERS = [
  "hermsywormsyjs@hotmail.com",   // Josh's forwarding address
  "josh@brain-de-le-jstew.com",   // future
];

export default {
  async email(message, env, ctx) {
    const from = message.from;
    const subject = message.subject || "(no subject)";
    const timestamp = Date.now();
    
    // Sanitize for key name
    const safeSubject = subject.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 60);
    const fromUser = from.split("@")[0].replace(/[^a-zA-Z0-9]/g, "_");
    const key = `incoming/${timestamp}-${fromUser}-${safeSubject}`;

    // 1. Save raw .eml for attachment processing
    const rawContent = await message.raw();
    await env.EMAIL_BUCKET.put(`${key}.eml`, rawContent, {
      httpMetadata: { contentType: "message/rfc822" },
    });

    // 2. Save structured JSON for quick parsing
    const payload = {
      from,
      to: Array.isArray(message.to) ? message.to.join(", ") : message.to,
      subject,
      timestamp,
      headers: Object.fromEntries(message.headers?.entries() || []),
      text: await message.text() || "",
      html: await message.html() || "",
      hasAttachments: message.attachments?.length > 0 || false,
      attachmentKeys: [],
    };

    // 3. Save attachments separately
    if (message.attachments?.length > 0) {
      for (let i = 0; i < message.attachments.length; i++) {
        const att = message.attachments[i];
        const attKey = `${key}_att_${i}_${att.filename || "unnamed"}`;
        const attBuffer = await att.bytes();
        await env.EMAIL_BUCKET.put(attKey, attBuffer, {
          httpMetadata: { 
            contentType: att.contentType || "application/octet-stream",
            contentDisposition: `attachment; filename="${att.filename || "unnamed"}"`,
          },
        });
        payload.attachmentKeys.push(attKey);
      }
    }

    // 4. Save the metadata (without HTML to keep it reasonable)
    const metaPayload = { ...payload };
    delete metaPayload.html;
    await env.EMAIL_BUCKET.put(`${key}.json`, JSON.stringify(metaPayload, null, 2), {
      httpMetadata: { contentType: "application/json" },
    });

    console.log(`Email saved: ${payload.subject} → ${key}`);
    console.log(`  From: ${from}`);
    console.log(`  Attachments: ${payload.attachmentKeys.length}`);
  },
};
