import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"
import { FiBox, FiPercent, FiBriefcase, FiHome, FiSettings, FiUsers, FiUser, FiSmile, FiCreditCard, FiShoppingBag, FiShoppingCart, FiTruck } from "react-icons/fi"

import type { UserPublic } from "../../client"

const menuItems = [
  { icon: FiHome, titleKey: "navigation.dashboard", path: "/" },
  { icon: FiCreditCard, titleKey: "menu.accounts", path: "/accounts" },
  { icon: FiShoppingBag, titleKey: "menu.stores", path: "/stores" },
  { icon: FiUser, titleKey: "erp.suppliers", path: "/suppliers" },
  { icon: FiSmile, titleKey: "erp.customers", path: "/customers" },
  { icon: FiBriefcase, titleKey: "navigation.items", path: "/items" },
  { icon: FiBox, titleKey: "menu.itemCategories", path: "/item_categories" },
  { icon: FiPercent, titleKey: "menu.itemUnits", path: "/item_units" },
  { icon: FiBox, titleKey: "menu.customerTypes", path: "/customer_types" },
  { icon: FiShoppingCart, titleKey: "erp.purchases", path: "/purchases" },
  { icon: FiTruck, titleKey: "erp.sales", path: "/sales" },
  { icon: FiSettings, titleKey: "menu.userSettings", path: "/settings" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const textColor = useColorModeValue("ui.main", "ui.light")
  const bgActive = useColorModeValue("#E2E8F0", "#4A5568")
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems = currentUser?.is_superuser
    ? [...menuItems, { icon: FiUsers, titleKey: "navigation.admin", path: "/admin" }]
    : menuItems

  const listItems = finalItems.map(({ icon, titleKey, path }) => (
    <Flex
      as={Link}
      to={path}
      w="100%"
      p={2}
      key={titleKey}
      activeProps={{
        style: {
          background: bgActive,
          borderRadius: "12px",
        },
      }}
      color={textColor}
      onClick={onClose}
    >
      <Icon as={icon} alignSelf="center" />
      <Text ml={2}>{t(titleKey)}</Text>
    </Flex>
  ))

  return (
    <>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
