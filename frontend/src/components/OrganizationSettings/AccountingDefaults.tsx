import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Select,
  Text,
  useColorModeValue,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import {
  type ApiError,
  type DefaultAccountsUpdate,
  AccountsService,
  OrganizationSettingsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

const AccountingDefaults = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const color = useColorModeValue("inherit", "ui.light")
  const showToast = useCustomToast()

  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ["organizationSettings"],
    queryFn: () => OrganizationSettingsService.getSettings(),
  })

  const { data: accountsData, isLoading: accountsLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts({ limit: 1000 }),
  })

  const accounts = accountsData?.data || []

  const {
    register,
    handleSubmit,
    formState: { isSubmitting, isDirty },
  } = useForm<DefaultAccountsUpdate>({
    mode: "onBlur",
    values: settings ? {
      default_clients_account_id: settings.default_clients_account_id,
      default_suppliers_account_id: settings.default_suppliers_account_id,
      default_vat_purchases_account_id: settings.default_vat_purchases_account_id,
      default_vat_sales_account_id: settings.default_vat_sales_account_id,
      default_revenue_account_id: settings.default_revenue_account_id,
      default_cash_account_id: settings.default_cash_account_id,
      default_bank_account_id: settings.default_bank_account_id,
    } : undefined,
  })

  const updateMutation = useMutation({
    mutationFn: (data: DefaultAccountsUpdate) =>
      OrganizationSettingsService.updateDefaultAccounts({ requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("settings.accounts.saved"), "success")
      queryClient.invalidateQueries({ queryKey: ["organizationSettings"] })
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
  })

  const onSubmit: SubmitHandler<DefaultAccountsUpdate> = async (data) => {
    // Convert empty strings to null
    const cleanedData: DefaultAccountsUpdate = {}
    for (const [key, value] of Object.entries(data)) {
      (cleanedData as Record<string, string | null>)[key] = value === "" ? null : value
    }
    updateMutation.mutate(cleanedData)
  }

  if (settingsLoading || accountsLoading) {
    return <Text>{t("common.loading")}</Text>
  }

  const accountFields = [
    { key: "default_clients_account_id", label: t("settings.accounts.clients") },
    { key: "default_suppliers_account_id", label: t("settings.accounts.suppliers") },
    { key: "default_vat_purchases_account_id", label: t("settings.accounts.vatPurchases") },
    { key: "default_vat_sales_account_id", label: t("settings.accounts.vatSales") },
    { key: "default_revenue_account_id", label: t("settings.accounts.revenue") },
    { key: "default_cash_account_id", label: t("settings.accounts.cash") },
    { key: "default_bank_account_id", label: t("settings.accounts.bank") },
  ]

  return (
    <Container maxW="full">
      <Heading size="sm" py={4}>
        {t("settings.accounts.title")}
      </Heading>
      <Text color="gray.500" mb={4}>
        {t("settings.accounts.description")}
      </Text>
      <Box
        w={{ sm: "full", md: "50%" }}
        as="form"
        onSubmit={handleSubmit(onSubmit)}
      >
        {accountFields.map(({ key, label }) => (
          <FormControl key={key} mb={4}>
            <FormLabel color={color}>{label}</FormLabel>
            <Select
              {...register(key as keyof DefaultAccountsUpdate)}
              placeholder={t("settings.accounts.selectAccount")}
            >
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.code} - {account.name}
                </option>
              ))}
            </Select>
          </FormControl>
        ))}

        <Flex mt={6} gap={3}>
          <Button
            variant="primary"
            type="submit"
            isLoading={isSubmitting || updateMutation.isPending}
            isDisabled={!isDirty}
          >
            {t("common.save")}
          </Button>
        </Flex>
      </Box>
    </Container>
  )
}

export default AccountingDefaults
