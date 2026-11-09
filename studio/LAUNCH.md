# Launch checklist

Work through it in order. **You** = things only you can do (accounts, money, legal). **Claude** = send me the details and I'll do it.

## 1. Decide and set up accounts (you)

- [ ] **Business name.** Check that the `.co.za` address is free (any registrar's search works), then register it.
- [ ] **Business email** on that address, e.g. `hello@yourname.co.za`. Zoho Mail's free plan, Google Workspace or your registrar's mail all work.
- [ ] **WhatsApp Business** on the number you'll use for the business.
- [ ] **Bank account for EFT.** A separate business or second account keeps wedding payments easy to track.
- [ ] **Yoco account** with online payments / payment links switched on (there's a once-off signup fee). Make one test payment link to yourself.
- [ ] **GitHub:** create an empty repository for the business site, e.g. `yourname-site`, and give Claude access to it.
- [ ] **Legal pages:** decide whether you're VAT-registered, fill in the highlighted placeholders in `terms.html` and `privacy.html` (or send them to me), and ideally have someone qualified read them once.

## 2. Fill in and move the site (Claude, once you send the details)

- [ ] Put the business name, email, WhatsApp number and order-form endpoint in `studio/js/studio.js`.
- [ ] Fill in the placeholders on the legal pages.
- [ ] Move `studio/` and `builder/` into the new repository, with the sales site at the top level.
- [ ] Update the demo links, and add a favicon and a link-preview image (so it looks good when shared on WhatsApp).
- [ ] Switch on GitHub Pages with your domain.

## 3. Point the domain at the site (you, about 10 minutes at your registrar)

In your domain's DNS settings, add:

| Type | Name | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | `<your-github-username>.github.io` |

Changes can take a few hours to spread. Then tick **Enforce HTTPS** in the repository's Pages settings.

## 4. Dress rehearsal before telling anyone

- [ ] Set `formEndpoint` to `https://formsubmit.co/ajax/<your email>`, submit a test order and click **Activate** in the email FormSubmit sends.
- [ ] Place a full fake order (Essential and Bespoke), check the email arrives with the build file, and paste it to Claude to build.
- [ ] Publish that test site the way a real client site will be (own repository + domain) and send a test RSVP.
- [ ] Send yourself a small Yoco payment link and an EFT, to check both reach your account.
- [ ] Open everything on a phone, because that's where couples and guests will see it.

## 5. Launch

- [ ] **Real examples:** offer one or two friends' weddings a discount in exchange for permission to show their site, and replace the placeholder demos.
- [ ] Google Business Profile, plus an Instagram / Facebook page using the envelope-opening animation as your hero video.
- [ ] Introduce yourself to venues, planners and photographers. They're asked about wedding websites all the time.

## For every client after launch

1. The couple fills in the questionnaire, and you receive the email with the build file.
2. Send the Yoco link and EFT details for the 50% deposit.
3. Paste the build file to Claude, which builds the site and gives you a checklist.
4. Hold the developer session(s), then collect the balance.
5. Register their web address, publish the site to its own repository, point the domain, and activate their RSVP emails.
6. Diary a reminder for when the site goes offline (3 or 12 months after the wedding).
