import {
  Container,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import type { UserPublic } from "../../client"
import Appearance from "../../components/UserSettings/Appearance"
import ChangePassword from "../../components/UserSettings/ChangePassword"
import DeleteAccount from "../../components/UserSettings/DeleteAccount"
import UserInformation from "../../components/UserSettings/UserInformation"
import {
  SmtpSettings,
  AzureSettings,
  AccountingDefaults,
} from "../../components/OrganizationSettings"

const userTabsConfig = [
  { titleKey: "settings.tabs.profile", component: UserInformation },
  { titleKey: "settings.tabs.password", component: ChangePassword },
  { titleKey: "settings.tabs.appearance", component: Appearance },
  { titleKey: "settings.tabs.danger", component: DeleteAccount },
]

const orgTabsConfig = [
  { titleKey: "settings.tabs.smtp", component: SmtpSettings },
  { titleKey: "settings.tabs.azure", component: AzureSettings },
  { titleKey: "settings.tabs.accounts", component: AccountingDefaults },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
})

function UserSettings() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  // Remove "Danger zone" for superusers
  const userTabs = currentUser?.is_superuser
    ? userTabsConfig.slice(0, 3)
    : userTabsConfig

  // Combine user tabs with organization tabs
  const allTabs = [...userTabs, ...orgTabsConfig]

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        {t("settings.title")}
      </Heading>
      <Tabs variant="enclosed">
        <TabList flexWrap="wrap">
          {allTabs.map((tab, index) => (
            <Tab key={index}>{t(tab.titleKey)}</Tab>
          ))}
        </TabList>
        <TabPanels>
          {allTabs.map((tab, index) => (
            <TabPanel key={index}>
              <tab.component />
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>
    </Container>
  )
}
