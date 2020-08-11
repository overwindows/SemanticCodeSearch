import Content from './content'
import React from 'react'
import theme, { GlobalStyle } from './theme'
import { ThemeProvider } from 'styled-components'

const App = () => (
  <ThemeProvider theme={theme}>
    <GlobalStyle />
    <Content />
  </ThemeProvider>
)

export default App
