import { createGlobalStyle } from 'styled-components'

export default createGlobalStyle`
  @import url("https://fonts.googleapis.com/css?family=Roboto:300,400,500,700,700i");

  *, *:before, *:after {
    box-sizing: inherit;
    margin: 0;
    padding: 0;
  }

  html {
    font-family: "Roboto", sans-serif;
    font-weight: 300;
    line-height: 1.5;
    text-align: left;
    color: ${({ theme }) => theme.primaryText};
    background: ${({ theme }) => theme.background};
    text-rendering: optimizeLegibility;
    box-sizing: border-box;
    -moz-osx-font-smoothing: grayscale;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: antialiased;
  }

  html, body, body > div {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
  }

  h1 {
    font-weight: 400;
  }

  h2 {
    font-size: 2.125rem;
    padding: 0 1rem;
  }

  h3 {
    font-size: 1.5rem;
    padding: 0 0.5rem;
    font-weight: 300;
  }

  p {
    color: ${({ theme }) => theme.secondaryText};
  }

  a {
    color: ${({ theme }) => theme.primary};
    text-decoration: none;
  }

  button {
    background: transparent;
    border: none;

    :active {
      outline: none;
    }
  }

  ul {
    flex-wrap: wrap;
    list-style-type: none;
  }

  :focus {
    outline: ${({ theme }) => theme.primary} auto 5px;
  }

  ::selection {
    background: ${({ theme }) => theme.primary}25;
  }
`
