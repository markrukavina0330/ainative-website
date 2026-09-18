# Leads by email — setup (about two minutes, no database)

Every Evaluation request — from the two forms on the site and from the agent's booking card — is delivered as an email to mark@ainative.ai by Web3Forms, a free form-to-email service that needs no account dashboard, no server, and no database. The site already contains the code; it only needs your access key.

1. Open https://web3forms.com in a browser. In the box on the home page, type **mark@ainative.ai** and click **Create Access Key**.
2. Check the mark@ainative.ai inbox. The email from Web3Forms contains a key that looks like `a1b2c3d4-…`. Click the verification link in that email if it asks you to.
3. Open the file `js/config.js` in the site folder in Notepad. Find the line that reads
   `"formAccessKey": "",`
   and paste the key between the quotes:
   `"formAccessKey": "a1b2c3d4-…",`
   Save the file.
4. Upload the whole site folder to Spaceship as usual (the `js` folder must be included).
5. Test: open https://ainative.ai/evaluation.html, submit the form with your own details. Within a minute an email titled **Evaluation request from ainative.ai** arrives at mark@ainative.ai with every field the visitor filled in; the visitor's address is set as the reply-to, so you can answer them directly from that email.

Until the key is pasted, the button still works: it opens the visitor's own email app with the request addressed to mark@ainative.ai.

Notes: the free plan allows 250 submissions a month, which is far more than the Evaluation form will see; there is nothing to renew. Spam is filtered by a hidden honeypot field already in the form. If you ever want a copy of each lead somewhere else (a spreadsheet, HubSpot), Web3Forms can forward to it from its dashboard without touching the site.
