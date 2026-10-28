# Held-out evaluation

| prompt | n | token-F1 | length ratio (1.0 = as terse as humans) | AI-isms / reply |
|---|---|---|---|---|
| v1 | 24 | 0.253 | 1.64 | 0.08 |
| v20 | 24 | 0.259 | 1.46 | 0.00 |

### Side-by-side samples

**SYNTH_004 - client:** Hi, I'm a freelance graphic designer. Can I apply for DTV?

- **real:** 'Hello! Yes, freelancers and self-employed individuals can apply for the DTV. May I know your nationality and where your business is registered?'
- **v1:** "Yes, freelancers can usually apply under the remote worker route, as long as your income comes from clients outside Thailand. Which country are you applying from, and what's your nationality?"  _(F1 0.34)_
- **v20:** "Hi, thanks for reaching out! Freelance design work can fit the remote worker route, so you're in the right place. What's your nationality, and which country will you be applying from?"  _(F1 0.222)_

**SYNTH_004 - client:** I'm German. My business is registered in Germany. I have clients from various countries.

- **real:** "Great! For self-employed applicants, you'll need to demonstrate that your work is location-independent and you won't be working with Thai clients. Where do you plan to submit your application?"
- **v1:** "Thanks, that's helpful. As a freelancer you'd most likely go through the remote worker route, and our legal team will confirm exactly which client contracts or income proof they need. Are you planning to apply from Germany?"  _(F1 0.118)_
- **v20:** "Thanks, that's helpful. Since your clients are overseas, you'd likely go the remote worker route. The service fee is 18,000 THB including government fees for most countries. Will you apply from Germany?"  _(F1 0.156)_

**SYNTH_004 - client:** I'm currently in Malaysia. Can I apply here?

- **real:** "Yes, Malaysia is a good option! For self-employed applicants, you'll need:\n\n1. Business registration documents (translated to English if in German)\n2. Bank statements showing 500,000 THB equivalent for 3 months\n3. Client contracts or invoices from the past 3 months\n4. Proof of income showing payments from clients\n5. Passport and photo"
- **v1:** "Yes, you can apply from Malaysia. Our service fee there is 18,000 THB, which includes government fees. Our legal team will check whether your freelance income fits the remote worker route. You can upload your documents in the app here: [APP_LINK]. Review is free and takes 1-2 business days, and you only pay once it's approved."  _(F1 0.246)_
- **v20:** "Yes, you can apply from Malaysia! For a remote worker DTV from there, our service fee is 18,000 THB including all government fees.\nIf you'd like to start, sign up in our app at [APP_LINK] and upload your documents. Our legal team reviews them for free in 1-2 business days."  _(F1 0.333)_

**SYNTH_004 - client:** My business documents are in German. Do I need official translations?

- **real:** "Yes, for visa applications, all documents must be in Thai or English. You'll need official English translations done by a certified translator. The translations should be stamped or signed to confirm accuracy."
- **v1:** "Good question. I can't say for certain whether Malaysia requires official translations for German business documents, so our legal team will confirm that when they review your files. You can upload the German originals now at [APP_LINK]. The review is free and takes 1-2 business days, and they'll tell you exactly what needs translating."  _(F1 0.136)_
- **v20:** "I'd rather not guess on that one, since I can't confirm the exact translation rule for Malaysia. Our legal team reviews documents for free in 1-2 business days and will tell you if translations are needed. You can upload the German files now at [APP_LINK] so they can check them."  _(F1 0.143)_
