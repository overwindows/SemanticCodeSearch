import GlobalStyle from './global'
export { GlobalStyle }

const screens = {
  mobile: 720,
}

const colors = {
  black: '#202121',
  grayDark: '#6c7680',
  gray: '#e6eaea',
  grayLight: '#f9f9f9',
  white: '#ffffff',
  blueDark: '#20232a',
  blue: '#0366d6',
  blueLight: '#50c9ea',
  red: '#fd1015',
  green: '#31c452',
  yellow: '#f2e05a',
}

const theme = {
  primary: colors.blueLight,
  primaryText: colors.blueDark,
  secondaryText: colors.grayDark,
  background: colors.grayLight,
  light: colors.white,
  error: colors.red,
}

export default {
  screens,
  colors,
  ...theme,
}
