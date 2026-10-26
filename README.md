# Felipe G. Bogo — Personal Website

Personal academic website of Felipe G. Bogo, featuring research in differential geometry and geometric analysis, publications, class notes, and a Catholic doctrine course. The interface is available in Portuguese and English.

**Visit the website:** [felipegbogo.github.io](https://felipegbogo.github.io/)

## About the website

The site brings together my academic work, teaching materials, and contact information. Its classical visual style combines serif typography with mathematical surfaces drawn as blue SVG wireframes.

The layout adapts to desktop, tablet, and mobile screens, with fluid text sizes and support for light and dark color schemes. Visitors can switch between Portuguese and English; their language preference is saved in their browser. Linked documents retain their original language.

## Sections

- **Homepage:** a short biography, education and research visits, and links to my CV and Lattes profile.
- **Publications:** published papers, ongoing doctoral research, and my master's dissertation and related materials.
- **Class Notes:** mathematics notes and problem sets, currently covering algebra and topology.
- **Catholic Doctrine:** Lesson 0, “Como fazer perguntas lendo livros?”, opens in an expandable card with a scrollable reading area, complete notes, and reference links. The lesson remains in its original Portuguese when the interface language changes.
- **Contact:** email addresses and institutional information.

## Mathematical illustrations

| Section | Surface |
| --- | --- |
| Homepage | Catenoid |
| Publications | Costa minimal surface |
| Class Notes | Torus of revolution |
| Contact | Sphere with great-circle geodesics |
| Catholic Doctrine | No surface |

The drawings are generated from mathematical formulas, with no stock images or rendering libraries. The catenoid is drawn in `index.html`; the torus and sphere are drawn in `assets/surfaces.js`. That file also includes a helicoid reserved for Miscellanea, which remains hidden.

The Costa illustration is generated numerically from its Weierstrass representation, following O. Michael Melko's [Visualizing Minimal Surfaces (2010)](https://content.wolfram.com/sites/19/2010/12/Melko.pdf). Its reproducible Python generator, mathematical references, and finite truncation details are documented in `scripts/generate_costa.py`.

## Source files

| File | Purpose |
| --- | --- |
| `index.html` | Page structure, styling, bilingual content, navigation, and the catenoid drawing. |
| `assets/surfaces.js` | Parametric torus and sphere drawings, plus the reserved helicoid. |
| `assets/surfaces/costa.svg` | Generated Costa illustration, with light and dark color schemes. |
| `scripts/generate_costa.py` | Reproducible Costa generator and mathematical references. |
| `docs/doctrine/Capitulo_0_Como_fazer_perguntas_lendo_livros.md` | Original Portuguese text of Lesson 0. |
| `assets/doctrine-lesson.js` | Formatted lesson content used by the inline reader. |
| `scripts/build_doctrine_lesson.py` | Dependency-free generator for the formatted lesson. |
| `docs/CV_Felipe_G_Bogo.pdf` | Compiled CV, opened in a new tab from the homepage. |
| `docs/README.md` | Instructions for updating documents. |

The website uses plain HTML, CSS, and JavaScript. It requires no package installation or build step.
