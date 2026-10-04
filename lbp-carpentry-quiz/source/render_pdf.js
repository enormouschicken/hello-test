const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'dist', 'print.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const loaded = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v, i, a) => a.indexOf(v) === i));
  await page.pdf({
    path: path.join(__dirname, 'dist', 'LBP-Carpentry-Practice-Quiz.pdf'),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-family:Arial,sans-serif;font-size:7.5px;color:#55625C;padding:0 14mm;display:flex;justify-content:space-between"><span>LBP Carpentry practice assessment · checked October 2026</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
    margin: { top: '15mm', bottom: '17mm', left: '14mm', right: '14mm' },
  });
  await browser.close();
  console.log('fonts:', loaded.join(', '));
})();
