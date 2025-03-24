const puppeteer = require("puppeteer");

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  }); // Connect to Chrome
  const page = await browser.newPage(); // Create a new page

  // Enable console messages on the page
  page
    .on("console", (msg) => {
      console.log("Console:", msg.text());
    })
    .on("pageerror", ({ message }) => console.log(message))
    .on("response", (response) =>
      console.log(`${response.status()} ${response.url()}`)
    )
    .on("requestfailed", (request) =>
      console.log(`${request.failure().errorText} ${request.url()}`)
    );

  await page.goto(process.argv[2]); // Navigate to a webpage

})();