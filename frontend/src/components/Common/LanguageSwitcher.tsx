import {
  Box,
  IconButton,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Text,
  HStack,
} from "@chakra-ui/react"
import { useTranslation } from "react-i18next"

const languages = [
  { code: "bg", name: "Български", flag: "🇧🇬" },
  { code: "en", name: "English", flag: "🇬🇧" },
]

const LanguageSwitcher = () => {
  const { i18n } = useTranslation()

  const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0]

  const changeLanguage = (langCode: string) => {
    i18n.changeLanguage(langCode)
  }

  return (
    <Box
      display={{ base: "none", md: "block" }}
      position="fixed"
      top={4}
      right={16}
    >
      <Menu>
        <MenuButton
          as={IconButton}
          aria-label="Change language"
          icon={<Text fontSize="18px">{currentLanguage.flag}</Text>}
          bg="ui.main"
          isRound
          data-testid="language-menu"
        />
        <MenuList>
          {languages.map((lang) => (
            <MenuItem
              key={lang.code}
              onClick={() => changeLanguage(lang.code)}
              bg={i18n.language === lang.code ? "ui.light" : "transparent"}
            >
              <HStack spacing={2}>
                <Text fontSize="20px">{lang.flag}</Text>
                <Text>{lang.name}</Text>
              </HStack>
            </MenuItem>
          ))}
        </MenuList>
      </Menu>
    </Box>
  )
}

export default LanguageSwitcher
