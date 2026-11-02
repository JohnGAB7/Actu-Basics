// Imprime programme.html en PDF A4 avec le Chromium de Playwright.
// Usage : node programme/imprimer_pdf.js <entree.html> <sortie.pdf>
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [entree, sortie] = process.argv.slice(2);
  if (!entree || !sortie) {
    console.error('Usage : node imprimer_pdf.js <entree.html> <sortie.pdf>');
    process.exit(2);
  }
  const navigateur = await chromium.launch();
  const page = await navigateur.newPage();
  await page.goto('file://' + path.resolve(entree), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: sortie,
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate:
      '<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5px;color:#5b6b80;padding:0 15mm;display:flex;justify-content:space-between">' +
      '<span>ACTU-BASICS · Programme éditorial et pédagogique · document de travail</span>' +
      '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  await navigateur.close();
})().catch((err) => { console.error(err); process.exit(1); });
