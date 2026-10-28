# Held-out evaluation

| prompt | turns | token-F1 | Δ F1 vs v1 (95% CI) | length ratio (1.0 = as terse as humans) | AI-isms / reply |
|---|---|---|---|---|---|
| v1 | 24 | 0.269 | - | 1.67 | 0.04 |
| v23 | 24 | 0.245 | -0.024 [-0.047, -0.005] ▼ | 1.58 | 0.01 |
| v1+rule | 24 | 0.259 | -0.010 [-0.029, +0.011] | 1.24 | 0.00 |

3 repeat(s) per turn, temperature 0.7; ▲/▼ = 95% CI excludes 0, no mark = not distinguishable from noise.

### Side-by-side samples (first repeat)

**SYNTH_004 - client:** Hi, I'm a freelance graphic designer. Can I apply for DTV?

- **real:** 'Hello! Yes, freelancers and self-employed individuals can apply for the DTV. May I know your nationality and where your business is registered?'
- **v1:** 'Yes, freelancers can usually apply under the remote worker route, as long as your work is for clients outside Thailand. Are you applying from your home country or from somewhere else right now?'  _(F1 0.321)_
- **v23:** "Hi! Yes, freelance work can fit the remote worker route for the DTV. What's your nationality, and which country are you planning to apply from?"  _(F1 0.375)_
- **v1+rule:** "Hi! Yes, freelancers can apply for the DTV as remote workers, as long as your work is done for clients outside Thailand. Which country are you applying from, and what's your nationality?"  _(F1 0.436)_

**SYNTH_004 - client:** I'm German. My business is registered in Germany. I have clients from various countries.

- **real:** "Great! For self-employed applicants, you'll need to demonstrate that your work is location-independent and you won't be working with Thai clients. Where do you plan to submit your application?"
- **v1:** "Thanks, that helps. You'd most likely apply under the remote worker route, with about 500,000 THB equivalent in a bank account for the last 3 months. Our legal team will confirm which client contracts or invoices work as income proof for freelancers. Will you be applying from Germany?"  _(F1 0.15)_
- **v23:** "Thanks, that helps. Freelancing for clients abroad usually fits the remote worker route. Are you living in Germany right now, or somewhere else you'd apply from?"  _(F1 0.14)_
- **v1+rule:** 'Good to know, thanks! Freelancers usually go the remote worker route, so contracts or letters from your clients will matter. Our legal team will confirm the exact list. You can upload your documents for a free review here: [APP_LINK]'  _(F1 0.169)_

**SYNTH_004 - client:** I'm currently in Malaysia. Can I apply here?

- **real:** "Yes, Malaysia is a good option! For self-employed applicants, you'll need:\n\n1. Business registration documents (translated to English if in German)\n2. Bank statements showing 500,000 THB equivalent for 3 months\n3. Client contracts or invoices from the past 3 months\n4. Proof of income showing payments from clients\n5. Passport and photo"
- **v1:** "Yes, you can apply from Malaysia. The service fee is 18,000 THB including government fees. You'll need proof of address in Malaysia and about 500,000 THB equivalent in your bank account for the last 3 months, and euros work fine. Once you're ready, you can upload your documents in our app [APP_LINK]. Our legal team reviews them free within 1-2 business days."  _(F1 0.38)_
- **v23:** "Yes, you can apply from Malaysia since you're outside Thailand right now. Our service fee is 18,000 THB including government fees, and you'll need about 500,000 THB equivalent in a bank account for the last 3 months.\n\nThe quickest start is uploading your documents at [APP_LINK]. Our legal team reviews them for free in 1-2 business days, and you only pay once it's approved."  _(F1 0.374)_
- **v1+rule:** "Yes, you can apply from Malaysia. The service fee is 18,000 THB including government fees, and you'll need proof of your Malaysian address. Want the app link so you can upload your documents for a free legal review?"  _(F1 0.319)_

**SYNTH_004 - client:** My business documents are in German. Do I need official translations?

- **real:** "Yes, for visa applications, all documents must be in Thai or English. You'll need official English translations done by a certified translator. The translations should be stamped or signed to confirm accuracy."
- **v1:** "I don't want to guess on the exact translation rule for German documents. Our legal team checks that during the free review, usually within 1-2 business days. Upload what you have at [APP_LINK] and they'll tell you exactly what needs translating."  _(F1 0.107)_
- **v23:** "I don't want to guess on that one, so our legal team will confirm whether your German documents need official translations. You can upload them to the app now as they are: [APP_LINK]. Legal reviews them in 1-2 business days, free, and will flag anything that needs translating."  _(F1 0.195)_
- **v1+rule:** "Not sure yet which ones need translating or certifying, so our legal team will confirm that. You can upload what you have at [APP_LINK] now, and they'll review it for free within 1-2 business days."  _(F1 0.116)_

**SYNTH_004 - client:** What about client invoices? They're a mix of German and English.

- **real:** 'For invoices, we can work with a mix. The key is that the embassy can verify:\n\n1. The invoice amounts match deposits in your bank statement\n2. The clients are not Thailand-based\n3. The dates are within the last 3 months\n\nIf any invoices need translation, please get those done as well.'
- **v1:** "The English invoices should be fine as they are. The German ones will need the same certified English translation as your business documents. Our legal team will confirm the details when they review, so you can upload what you have at [APP_LINK] and they'll tell you if anything's missing."  _(F1 0.233)_
- **v23:** "I can't say for sure whether mixed German and English invoices are fine, since our legal team makes that call when they review the file. Upload them to the app at [APP_LINK] and they'll review everything for free within 1-2 business days, including whether any of them need translating."  _(F1 0.212)_
- **v1+rule:** 'English invoices are fine as they are. The German ones will need English translations, same as your business registration. Our legal team will confirm the exact format during their free review. You can upload everything here: [APP_LINK]'  _(F1 0.198)_

**SYNTH_004 - client:** One of my clients is actually a Thai company. Is that a problem?

- **real:** 'Yes, this could be problematic. One of the most important rules for the DTV is that you cannot work with Thai clients, suppliers, or companies. We recommend not including any invoices or contracts from Thai clients in your application.\n\nDo you have enough invoices from non-Thai clients to demonstrate your income?'
- **v1:** "Yes, that's a problem for the DTV. It doesn't allow work for Thai companies or Thai clients, so that contract would need to be sorted out before you apply. Is that company paying you directly, or through an entity outside Thailand? Our legal team can confirm what options you have."  _(F1 0.353)_
- **v23:** "Yes, that can be a problem. The DTV is for remote work for clients outside Thailand, so a Thai company doesn't fit that. Please don't leave it out of your application, though. Mention it when you upload your documents in the app so our legal team can tell you how it affects your case: [APP_LINK]"  _(F1 0.333)_
- **v1+rule:** "Yes, that's a problem. The DTV doesn't allow work for Thai companies or Thai clients, so that contract would need to be stopped or handled under a different visa. Our legal team can check how it affects your application."  _(F1 0.352)_
