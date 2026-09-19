const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function run() {
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const executablePath = fs.existsSync(chromePath) ? chromePath : edgePath;

  const browser = await puppeteer.launch({
    executablePath,
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,850']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 850 });

  await page.goto('http://localhost:8000', { waitUntil: 'networkidle0' });

  // 1. Open Target Combobox, search "port"
  await page.click('#target-combobox-trigger');
  await page.waitForSelector('#target-combobox-panel:not(.hidden)', { visible: true });
  await page.type('#target-search-input', 'port', { delay: 40 });
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(__dirname, 'combobox_search_port.png') });

  // 2. Select Portuguese
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 400));

  // 3. Swap
  await page.click('#swap-lang-btn');
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(__dirname, 'combobox_swapped_portuguese.png') });

  // 4. Test gTTS Unsupported check: Select Hebrew ('he') as target
  await page.click('#target-combobox-trigger');
  await page.waitForSelector('#target-combobox-panel:not(.hidden)', { visible: true });
  await page.type('#target-search-input', 'hebrew', { delay: 40 });
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(__dirname, 'combobox_hebrew_search.png') });

  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 400));

  const ttsBtnDisabled = await page.$eval('#tts-play-btn', b => b.disabled || b.classList.contains('opacity-40'));
  const ttsLabel = await page.$eval('#tts-voice-label', l => l.textContent.trim());
  console.log('Hebrew TTS Check -> Button Disabled:', ttsBtnDisabled, '| Label:', ttsLabel);
  await page.screenshot({ path: path.join(__dirname, 'combobox_hebrew_tts_disabled.png') });

  // 5. Switch target back to Spanish to restore normal state
  await page.click('#target-combobox-trigger');
  await page.waitForSelector('#target-combobox-panel:not(.hidden)', { visible: true });
  await page.type('#target-search-input', 'span', { delay: 40 });
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 400));

  await browser.close();
  console.log('All tests finished successfully!');
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
