# Held-out evaluation

| prompt | n | token-F1 | length ratio (1.0 = as terse as humans) | AI-isms / reply |
|---|---|---|---|---|
| v1 | 24 | 0.251 | 1.57 | 0.00 |
| v23 | 24 | 0.232 | 1.54 | 0.00 |

### Side-by-side samples

**SYNTH_004 - client:** Hi, I'm a freelance graphic designer. Can I apply for DTV?

- **real:** 'Hello! Yes, freelancers and self-employed individuals can apply for the DTV. May I know your nationality and where your business is registered?'
- **v1:** 'Yes, freelancers can usually apply under the remote worker route as long as your income comes from clients outside Thailand. Are you currently living outside Thailand, and which country would you apply from?'  _(F1 0.25)_
- **v23:** "Hi! Yes, freelance work can fit the remote worker route for the DTV. What's your nationality, and which country are you planning to apply from?"  _(F1 0.375)_

**SYNTH_004 - client:** I'm German. My business is registered in Germany. I have clients from various countries.

- **real:** "Great! For self-employed applicants, you'll need to demonstrate that your work is location-independent and you won't be working with Thai clients. Where do you plan to submit your application?"
- **v1:** "Good news, Germany works well for this. Since you're freelancing, you'd usually go the remote worker route, and the exact proof for self-employed applicants (like client contracts or invoices) is something our legal team will confirm when they review your file.\n\nThe app is [APP_LINK]. You can upload your documents there, and the review is free and takes 1-2 business days. Are you planning to apply from Germany, or from somewhere else?"  _(F1 0.208)_
- **v23:** "Thanks, that helps. Are you currently living in Germany, or somewhere else? That tells us which embassy you'd apply through."  _(F1 0.078)_

**SYNTH_004 - client:** I'm currently in Malaysia. Can I apply here?

- **real:** "Yes, Malaysia is a good option! For self-employed applicants, you'll need:\n\n1. Business registration documents (translated to English if in German)\n2. Bank statements showing 500,000 THB equivalent for 3 months\n3. Client contracts or invoices from the past 3 months\n4. Proof of income showing payments from clients\n5. Passport and photo"
- **v1:** 'Yes, you can apply from Malaysia. Our service fee is 18,000 THB including government fees. Start by uploading your documents in the app at [APP_LINK]. Our legal team reviews them free within 1-2 business days, and you only pay once the review is done.'  _(F1 0.255)_
- **v23:** "Yes, you can apply from Malaysia since you're outside Thailand. For German applicants the fee is 18,000 THB including government fees. Download our app at [APP_LINK] and upload your documents. Our legal team reviews them for free in 1-2 business days, and you only pay once approved. Also check that you have about 500,000 THB equivalent in a bank account for the last 3 months."  _(F1 0.371)_

**SYNTH_004 - client:** My business documents are in German. Do I need official translations?

- **real:** "Yes, for visa applications, all documents must be in Thai or English. You'll need official English translations done by a certified translator. The translations should be stamped or signed to confirm accuracy."
- **v1:** "I don't want to guess on this one, since the exact requirement can depend on the embassy. Our legal team will confirm whether your German documents need official translations for a Malaysia application.\n\nYou can upload them now at [APP_LINK]. The review is free and usually takes 1-2 business days, so they'll flag anything that needs translating."  _(F1 0.198)_
- **v23:** "I'm not certain whether German documents need official translations, so our legal team will confirm that when they review your file. You can upload the originals now at [APP_LINK], and they'll tell you if a translation is needed. Their review is free and takes 1-2 business days."  _(F1 0.173)_

**SYNTH_004 - client:** What about client invoices? They're a mix of German and English.

- **real:** 'For invoices, we can work with a mix. The key is that the embassy can verify:\n\n1. The invoice amounts match deposits in your bank statement\n2. The clients are not Thailand-based\n3. The dates are within the last 3 months\n\nIf any invoices need translation, please get those done as well.'
- **v1:** "English invoices can go in as they are. The German ones will need the same certified English translation as your business registration, so you can get those done together. Our legal team reviews documents for free in 1-2 business days, so you can upload what you have now at [APP_LINK] and they'll flag anything else they need."  _(F1 0.304)_
- **v23:** "I can't say for sure which invoices need translating, so I'd rather not guess. Our legal team checks that during the free review, which takes 1-2 business days. You can upload them as they are now at [APP_LINK], and legal will tell you if any German ones need an English translation. The translation details I gave earlier should also be confirmed by them."  _(F1 0.254)_

**SYNTH_004 - client:** One of my clients is actually a Thai company. Is that a problem?

- **real:** 'Yes, this could be problematic. One of the most important rules for the DTV is that you cannot work with Thai clients, suppliers, or companies. We recommend not including any invoices or contracts from Thai clients in your application.\n\nDo you have enough invoices from non-Thai clients to demonstrate your income?'
- **v1:** "Yes, that's a problem for the DTV. It's meant for remote work for clients outside Thailand, so a Thai company as a client doesn't fit. Working for Thai entities would need a different visa and work permit. Is that work ongoing, or could you wrap it up before you apply?"  _(F1 0.275)_
- **v23:** "Yes, that's a real issue. The DTV is for work for clients outside Thailand, so a Thai company doesn't fit that route. Is that client registered in Thailand, or is it a foreign company with a Thai office or contact?"  _(F1 0.304)_

**SYNTH_004 - client:** Yes I have plenty from EU and US clients. Should I avoid mentioning the Thai client at all?

- **real:** "Exactly. Just submit documentation from your non-Thai clients. During any interview, if asked about your work, focus on your international clients only. The embassy may misunderstand and think you're trying to work in Thailand, which would lead to rejection."
- **v1:** "Plenty of EU and US invoices is a good sign. I wouldn't try to leave the Thai client out, though. Embassies can ask about your income sources, and a mismatch could hurt the application. Our legal team can tell you how to handle it. You can upload your documents at [APP_LINK], and they'll review them in 1-2 business days, free of charge."  _(F1 0.173)_
- **v23:** "Plenty of EU and US invoices is a good start. Leave the Thai client's invoices out of your document pack, but don't hide the relationship if the embassy or a form asks you directly. Answer those questions truthfully. Also, the DTV doesn't allow work for Thai clients during your stay, so check that this client's work will end.\n\nWant the app link so you can upload your documents for our legal team to review? It's free, and you only pay after approval."  _(F1 0.23)_

**SYNTH_004 - client:** Got it. What's the processing time in Malaysia?

- **real:** 'Processing in Malaysia typically takes 10-14 business days. Our service fee is 18,000 THB including government fees. Please upload your documents to our app and our legal team will review everything to ensure the highest chance of approval.'
- **v1:** "I don't have a confirmed processing time for Malaysia, so our legal team will give you the current timeline when they review your file. One correction to my earlier advice: please don't leave the Thai client out of the application. Our legal team should look at that connection before you submit, so you can upload your documents at [APP_LINK] and they'll review them within 1-2 business days, free."  _(F1 0.345)_
- **v23:** "I don't have a confirmed processing time for Malaysia, and I'd rather not guess. Our legal team can confirm it once they've reviewed your file.\n\nI also need to correct something from earlier: please don't leave out the Thai client or hold back that information if the embassy asks. Flag it to the legal team when you upload at [APP_LINK] so they can advise you on it."  _(F1 0.241)_

**SYNTH_004 - client:** Perfect. I'll get the translations done and upload everything this week.

- **real:** "Sounds great! Once you've uploaded, share your email with us so we can prioritize your case. We'll review within 1-2 business days and provide feedback. Good luck!"
- **v1:** "Sounds good, thanks! One correction from earlier: please don't leave the Thai client out on purpose. Mention them in the app and our legal team will tell you how to handle that invoice.\n\nYou can upload everything at [APP_LINK]. Review takes 1-2 business days, and you only pay after approval."  _(F1 0.225)_
- **v23:** "Sounds like a good plan. Sign up at [APP_LINK] and upload what you have so our legal team can start reviewing. Before you send anything, please don't leave the Thai client out of your file. Our legal team should look at that one with you, and it's better they see the full picture from the start."  _(F1 0.165)_

**SYNTH_008 - client:** Hi my documents were approved. Ready to pay but having issues with the payment.

- **real:** "Hello! I'm sorry to hear you're having payment issues. What problem are you experiencing?"
- **v1:** "Great news that your documents were approved! Sorry the payment is giving you trouble. What happens when you try: is there an error message, or does it just not go through? Please don't send any card details here, just describe what you see on the screen."  _(F1 0.133)_
- **v23:** "Nice, that's the good part done! Sorry, I mean, glad to hear it. Can you send me the email you signed up with so I can check your account? Don't include any card details here. Our team is on 10 AM to 6 PM Thailand time if it's faster to sort out there."  _(F1 0.119)_

**SYNTH_008 - client:** The card payment keeps failing. I tried 3 times already.

- **real:** "That's frustrating! Sometimes international card payments can be blocked by banks. Would you be able to pay via bank transfer instead?"
- **v1:** "Sorry about that, three failed tries is frustrating. Your bank sometimes blocks online payments to foreign merchants, so it's worth checking with them, or trying a different card if you have one. Do you see an error message on the screen? That'll help us figure out what's going wrong."  _(F1 0.2)_
- **v23:** "Congrats on the approval! Sorry the card keeps failing. Could you send the email address you signed up with in our app so I can look up your account? Please don't share any card details here."  _(F1 0.105)_

**SYNTH_008 - client:** Yes I can do transfer. What are the details?

- **real:** 'Great! Here are our bank transfer details:\n\nBank: [BANK_NAME]\nAccount Name: [ACCOUNT_NAME]\nAccount Number: [ACCOUNT_NUMBER]\nAmount: 18,000 THB\n\nPlease include your email address in the transfer reference so we can match the payment to your account.'
- **v1:** "Great, glad your documents came through! I don't want to send you the wrong account, so I'm getting the exact transfer details and amount for your file from our team. Please wait for those here before sending anything. Once you have them, we can get your application submitted."  _(F1 0.364)_
- **v23:** "Great, glad your documents are approved. I don't have the transfer details in front of me, so I'll get them confirmed for you. What's the email you signed up with? I'll pull up your account so the right details go to you."  _(F1 0.317)_

**SYNTH_008 - client:** Done! Just transferred. Here's the receipt. / [Non-text message]

- **real:** "Payment received, thank you! I've updated your account. We'll now proceed with submitting your application to the embassy."
- **v1:** "Got it, thanks for sending the receipt! We'll match the transfer to your account and confirm once it's come through on our side. Meanwhile, could you confirm your intended travel dates so we can line up the submission?"  _(F1 0.25)_
- **v23:** "Nice, thanks for sending that! We'll match the transfer to your account and confirm once it's come through. After that we'll move straight to submitting your DTV application. Did you put your email in the transfer reference?"  _(F1 0.327)_

**SYNTH_008 - client:** Great! How long until I hear back?

- **real:** "Processing time is typically 10-14 business days. We'll keep you updated on any progress or if the embassy requests additional documents. You can also check the status in our app anytime."
- **v1:** "Glad that's sorted! We can't give an exact date since embassy timing depends on them, but our team will submit your application and message you as soon as there's an update. If you have any questions in the meantime, just ask here."  _(F1 0.243)_
- **v23:** "Thanks for paying! We're submitting your application to the embassy next. I don't have a firm timeline for the decision, so our legal team can confirm that. We'll email you as soon as there's an update, and the approval will go to your email and the app."  _(F1 0.203)_

**SYNTH_008 - client:** Perfect. Do I need to do anything else?

- **real:** "Just a few reminders:\n\n1. Please remain in your submission country until the visa is approved for our money-back guarantee to apply\n2. Maintain the 500,000 THB balance in case they request an updated statement\n3. Keep your phone accessible in case we need to reach you urgently\n\nWe'll handle everything else!"
- **v1:** "Nothing else from you right now, we'll handle the submission. Just keep the 500,000 THB in your bank account until the visa is approved, since the embassy can ask for an updated statement. We'll message you if anything else comes up."  _(F1 0.458)_
- **v23:** 'Nothing else needed from you right now, just two things. Keep your bank balance (about 500,000 THB equivalent) where it is until the visa is approved, and watch the app and your email in case the embassy asks for anything extra. Once approved, print the approval PDF to bring when you travel.'  _(F1 0.374)_

**SYNTH_008 - client:** Understood. Thanks for the quick help!

- **real:** "You're welcome! We'll be in touch soon. Our working hours are 10 AM to 6 PM Thailand time if you have any questions."
- **v1:** "You're welcome! Keep an eye on the app for any updates, and message us here if anything comes up while we're processing it."  _(F1 0.174)_
- **v23:** "You're welcome! We'll keep you updated in the app as things move along. Message us anytime if anything comes up."  _(F1 0.279)_

**SYNTH_012 - client:** Oh no, what do they need?

- **real:** "They're requesting:\n\n1. Updated bank statement (must be dated within 7 days)\n2. Entry/exit records from your country for the past year\n3. Additional proof of client payments matching your invoices"
- **v1:** "Don't worry, it's usually something routine. We don't have the exact list yet, so our legal team needs to read the embassy's message first. Could you upload the email or letter you received to our app at [APP_LINK]? They'll review it within 1-2 business days and tell you exactly what to send back."  _(F1 0.115)_
- **v23:** "Let's get you the exact list. I don't want to guess, and the embassy's message is the source of truth. Which embassy did you apply through, and is it the remote worker or soft-power route?"  _(F1 0.059)_

**SYNTH_012 - client:** The bank statement I can get. What about entry/exit records? How do I get those?

- **real:** "You can usually get entry/exit records from your country's immigration department. Some countries offer this online through their immigration website. Which country are you a citizen of?"
- **v1:** "Good, the bank statement is the easy part. I don't want to guess at the exact source for entry/exit records, since that depends on your country and what the embassy accepts. Our legal team can confirm that quickly. Which country are you applying from?"  _(F1 0.274)_
- **v23:** "Good that the bank statement is doable. I don't want to guess how to get the entry/exit records, since it depends on your country and file. What email did you sign up with? I'll pull up your account and flag it for the legal team to confirm the exact steps."  _(F1 0.177)_

**SYNTH_012 - client:** South Korea. Is there an online system?

- **real:** "Yes! For Korean citizens, you can get entry/exit records from the Korea Immigration Service website. You'll need your Korean ID to log in. The document should show all your international travel for the past 12 months."
- **v1:** "Yes, South Korea's Immigration Service has an online system called HiKorea (hikorea.go.kr), where you can request an entry and exit record certificate. Our legal team will confirm that it's the right document for the embassy's request and what period it needs to cover, so send it to them once you have it."  _(F1 0.264)_
- **v23:** "I don't have confirmed details on how Korean entry/exit records are requested, so I don't want to point you to the wrong place. Our legal team can confirm the exact steps for South Korea. Could you upload the embassy's request to [APP_LINK] so they can review it and tell you how to get those records?"  _(F1 0.277)_

**SYNTH_012 - client:** Found it! Downloading now. What format do they need?

- **real:** "A PDF printout is fine. Make sure it's dated - the embassy wants to see it was generated recently, ideally within a day or two of submission. Please upload it to the app once you have it."
- **v1:** "Glad you found it! I don't want to guess on the format, so our legal team will confirm exactly what the embassy accepts. Once you've got the record, upload it in the app and they'll check it against the request."  _(F1 0.289)_
- **v23:** "Nice, glad you found it! I don't have the exact format the embassy wants for the entry/exit records, so I won't guess. Save the file as you downloaded it and upload it to the app with your bank statement. Our legal team will check it and confirm if anything needs changing, usually within 1-2 business days."  _(F1 0.277)_

**SYNTH_012 - client:** Got it. What about the payment proof? I already sent invoices.

- **real:** 'The embassy wants to see that the invoice amounts match actual deposits in your bank statement. Can you provide:\n\n1. Bank statement highlighting the specific deposits\n2. Payment receipts or transfer confirmations from clients\n\nThe dates and amounts should match your invoices.'
- **v1:** "Invoices alone usually aren't enough, since the embassy wants to see the money actually arriving. Bank statements or transfer records showing payments from those clients, matched to the invoice numbers, are the usual approach. Our legal team will confirm the exact format they need. Do you have those transfer records handy?"  _(F1 0.344)_
- **v23:** "I can't say for sure which payment records the embassy will accept, so our legal team needs to confirm that. The quickest route is to upload your invoices and the embassy's request letter to the app at [APP_LINK]. They review within 1-2 business days. They'll also double-check the bank statement and entry record details I mentioned earlier."  _(F1 0.294)_

**SYNTH_012 - client:** Some payments have service fees deducted so amounts don't match exactly. Is that okay?

- **real:** "That's common and acceptable. If the amounts are slightly different due to fees, please provide any documentation showing the fee breakdown. We can explain this to the embassy - just make sure the dates align."
- **v1:** "Good question, and I don't want to guess on that one. Our legal team will confirm whether the embassy accepts it. In the meantime, try to get the transfer confirmations that show the original invoice amount and the fee that was deducted, so the difference is easy to see."  _(F1 0.217)_
- **v23:** "I can't say for sure whether the embassy will accept that, so let's have our legal team check it. Meanwhile, keep the transfer receipts or remittance advice from each client, since they show the full amount that was sent and the fee taken out. Send me the email you signed up with and I'll look at your account and pass this to the legal team today."  _(F1 0.2)_

**SYNTH_012 - client:** Okay I'll get everything together. How quickly do they need this?

- **real:** "Please try to submit within 3 business days. The embassy has a deadline for document requests. If we don't respond in time, they may reject the application."
- **v1:** "I don't have the embassy's exact deadline, so check the request letter for a date. If there isn't one, tell me and I'll have our legal team confirm. Since the bank statement needs to be recent, you could get that one first and upload what you have to [APP_LINK] as you go."  _(F1 0.2)_
- **v23:** "The embassy letter should state the exact deadline, so check that first and treat it as the priority. Start with the bank statement, since it's the quickest to get, then the entry/exit records. Our legal team can confirm the timing if the letter is unclear. Upload everything to the app as you go: [APP_LINK]"  _(F1 0.145)_

**SYNTH_012 - client:** Got it! I'll upload everything tonight. Thanks for the quick response!

- **real:** 'No problem! Once you upload, our team will review and submit to the embassy right away. Message us if you have any trouble getting any of the documents!'
- **v1:** "Sounds good, thanks for getting on it so fast! Once everything's in the app, our legal team will review it, usually within 1-2 business days. If anything's unclear while you're pulling it together, just message me here."  _(F1 0.273)_
- **v23:** "Sounds good, thanks for moving quickly. Once everything's uploaded, send me the email you signed up with so I can flag your case to the legal team. They'll confirm the exact requirements when they review it."  _(F1 0.219)_
