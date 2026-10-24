# Site pessoal de Felipe G. Bogo

Site estático com navegação em português e inglês. Não precisa instalar Node, dependências ou executar uma compilação.

## Acrescentar o currículo

O PDF do currículo não está incluído neste pacote. Copie o PDF já compilado que você possui para a pasta `docs` e use exatamente este nome:

`docs/CV_Felipe_G_Bogo.pdf`

O botão **CV** já aponta para esse arquivo. Ele funcionará depois que o PDF estiver nessa pasta e for enviado ao GitHub.

## Publicar pelo navegador

1. Descompacte o pacote no computador e acrescente o PDF na pasta `docs`.
2. No GitHub, crie um repositório público chamado `SEU_USUARIO.github.io`, substituindo `SEU_USUARIO` pelo seu nome de usuário. Se esse repositório já existir, use-o.
3. Abra o repositório e escolha **Add file → Upload files**. Em um repositório vazio, use o link para enviar um arquivo existente.
4. Envie o **conteúdo** da pasta deste pacote: `index.html`, `README.md` e a pasta `docs`, já com o PDF. O `index.html` deve ficar na raiz do repositório. Não envie o ZIP nem uma pasta externa envolvendo todos os arquivos.
5. Confirme o envio em **Commit changes**, na branch `main`.
6. Abra **Settings → Pages**. Em **Build and deployment**, escolha **Deploy from a branch**; em **Branch**, escolha `main` e a pasta `/ (root)`. Clique em **Save**.
7. Aguarde a publicação. Acompanhe a execução em **Actions** e abra o endereço mostrado em **Settings → Pages**. Para o nome de repositório acima, ele será `https://SEU_USUARIO.github.io/`.
8. Confira o seletor PT/EN, as seções, os links dentro da biografia e os botões **CV** e **CV Lattes**. Abra o CV para confirmar que o PDF foi enviado com o nome correto.

O pacote também contém `.nojekyll`, que pode ser enviado se estiver visível no seu seletor de arquivos. Sua ausência não impede este site simples de HTML de funcionar. Se você escolher um nome diferente para o repositório, o endereço terá também o nome dele: `https://SEU_USUARIO.github.io/NOME_DO_REPOSITORIO/`.

## Atualizar o conteúdo

- **Textos e links:** edite `index.html`. No bloco JavaScript, o objeto `imported` reúne biografia, formação, publicações, notas e contato. O objeto `text` contém os rótulos em português (`pt`) e inglês (`en`).
- **Currículo:** substitua `docs/CV_Felipe_G_Bogo.pdf`, mantendo o nome.
- **Notas e documentos novos:** coloque os PDFs em `docs` e acrescente os caminhos relativos correspondentes em `imported`. Os documentos já vinculados ao Drive e ao Dropbox continuam nos destinos originais.
- **Curso de Doutrina:** a seção está preparada com a aula introdutória. Os materiais do curso ainda precisam ser acrescentados; nenhum PDF de aula fictício foi incluído.
- **Aparência:** os estilos estão no início de `index.html`. O catenoide é desenhado a partir de sua parametrização matemática no próprio arquivo.

A preferência de idioma é guardada apenas no navegador do visitante. Ao reabrir o site, a seção inicial será a Homepage.

Referência: [documentação oficial do GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
