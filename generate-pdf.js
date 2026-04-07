const { chromium } = require('C:/Users/paulo/Workspaces/curso-claude-code/node_modules/playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const htmlPath = path.resolve(__dirname, 'planejamento-pdf.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });

  const pdfPath = path.resolve(__dirname, 'Tozi - Planejamento de Projeto.pdf');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '25mm', bottom: '25mm', left: '20mm', right: '20mm' },
    printBackground: true,
    displayHeaderFooter: false,
  });

  console.log(`PDF gerado: ${pdfPath}`);
  await browser.close();
})();
