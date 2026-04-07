const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const htmlPath = path.resolve(__dirname, 'relatorio-comportamental.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });

  const pdfPath = path.resolve(__dirname, 'Tozi - Relatório Comportamental IA.pdf');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '0mm', bottom: '0mm', left: '0mm', right: '0mm' },
    printBackground: true,
    displayHeaderFooter: false,
  });

  console.log(`PDF gerado: ${pdfPath}`);
  await browser.close();
})();
