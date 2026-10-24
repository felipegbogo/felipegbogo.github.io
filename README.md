# Felipe G. Bogo — Personal Website

Personal academic website of Felipe G. Bogo, featuring research in differential geometry and geometric analysis, publications, class notes, and a Catholic doctrine course. The interface is available in Portuguese and English.

**Visit the website:** [felipegbogo.github.io](https://felipegbogo.github.io/)

## About the website

The site brings together my academic work, teaching materials, and contact information. Its classical visual style uses serif typography and a catenoid drawn from its mathematical parametrization as an SVG wireframe.

The layout adapts to desktop, tablet, and mobile screens, with fluid text sizes and support for light and dark color schemes. Visitors can switch between Portuguese and English; their language preference is saved in their browser. Linked documents retain their original language.

## Sections

- **Homepage:** a short biography, education and research visits, and links to my CV and Lattes profile.
- **Publications:** published papers, ongoing doctoral research, and my master's dissertation and related materials.
- **Class Notes:** mathematics notes and problem sets, currently covering algebra and topology.
- **Catholic Doctrine:** an introductory session and a section prepared for future course notes, documents, and further reading.
- **Contact:** email addresses and institutional information.

## Source files

| File | Purpose |
| --- | --- |
| `index.html` | Page structure, styling, bilingual content, navigation, and the catenoid drawing. |
| `docs/CV_Felipe_G_Bogo.pdf` | Compiled CV, opened in a new tab from the homepage. |
| `docs/README.md` | Instructions for updating documents. |

The website uses plain HTML, CSS, and JavaScript. It requires no package installation or build step.

## Preview locally

From the repository directory, run:

```sh
python3 -m http.server 8000
```

Then open [localhost:8000](http://localhost:8000/) in your browser.

## Update the content

- Edit the `imported` object in `index.html` to update biographies, education, publications, class notes, and contact links.
- Edit the `text` object to update interface labels in Portuguese (`pt`) and English (`en`).
- Replace `docs/CV_Felipe_G_Bogo.pdf` to update the CV, keeping the same filename and capitalization.
- Add new PDFs to `docs/` and link to them using relative paths in `index.html`. Existing Google Drive and Dropbox links remain external.
- Update course content in the `course` branch of the `render()` function when new materials are ready.
- Edit the CSS and the surface drawing code in `index.html` to adjust the appearance.

## Deployment

This repository is published with [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

In **Settings → Pages**, the publishing source is **Deploy from a branch**, using the **main** branch and **/ (root)** folder. The `docs/` directory stores documents; the website entry point is `index.html` at the repository root.

Push changes to `main` to publish an update. Deployment progress is available under **Actions**, and the live address is shown in **Settings → Pages**.
