import '../styles/globals.css'
import { ThemeProvider, CSSReset } from "@chakra-ui/core"
import { theme } from "@chakra-ui/core";



const customTheme = {
  ...theme,
  colors: {
    ...theme.colors,
    brand: {
      900: "#1a365d",
      800: "#153e75",
			700: "#2a69ac",
    },
  },
};

function MyApp({ Component, pageProps }) {
  return (
   <ThemeProvider theme={customTheme}>
    <Component {...pageProps} />)
   </ThemeProvider>) 
}

export default MyApp
