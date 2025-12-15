import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  InputGroup,
  InputRightElement,
  NumberInput,
  NumberInputField,
  Switch,
  Text,
  useColorModeValue,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import {
  type ApiError,
  type SmtpSettingsUpdate,
  OrganizationSettingsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

const SmtpSettings = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const color = useColorModeValue("inherit", "ui.light")
  const showToast = useCustomToast()
  const [showPassword, setShowPassword] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ["organizationSettings"],
    queryFn: () => OrganizationSettingsService.getSettings(),
  })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { isSubmitting, isDirty },
  } = useForm<SmtpSettingsUpdate>({
    mode: "onBlur",
    values: settings ? {
      smtp_host: settings.smtp_host,
      smtp_port: settings.smtp_port,
      smtp_username: settings.smtp_username,
      smtp_password: settings.smtp_password,
      smtp_use_tls: settings.smtp_use_tls,
      smtp_from_email: settings.smtp_from_email,
      smtp_from_name: settings.smtp_from_name,
    } : undefined,
  })

  const useTls = watch("smtp_use_tls")

  const updateMutation = useMutation({
    mutationFn: (data: SmtpSettingsUpdate) =>
      OrganizationSettingsService.updateSmtpSettings({ requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("settings.smtp.saved"), "success")
      queryClient.invalidateQueries({ queryKey: ["organizationSettings"] })
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
  })

  const testMutation = useMutation({
    mutationFn: () => OrganizationSettingsService.testSmtpConnection(),
    onSuccess: (result) => {
      if (result.success) {
        showToast(t("common.success"), result.message, "success")
      } else {
        showToast(t("common.error"), result.message, "error")
      }
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
  })

  const onSubmit: SubmitHandler<SmtpSettingsUpdate> = async (data) => {
    updateMutation.mutate(data)
  }

  if (isLoading) {
    return <Text>{t("common.loading")}</Text>
  }

  return (
    <Container maxW="full">
      <Heading size="sm" py={4}>
        {t("settings.smtp.title")}
      </Heading>
      <Text color="gray.500" mb={4}>
        {t("settings.smtp.description")}
      </Text>
      <Box
        w={{ sm: "full", md: "50%" }}
        as="form"
        onSubmit={handleSubmit(onSubmit)}
      >
        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.host")}</FormLabel>
          <Input
            {...register("smtp_host")}
            placeholder="smtp.example.com"
          />
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.port")}</FormLabel>
          <NumberInput
            defaultValue={settings?.smtp_port || 587}
            min={1}
            max={65535}
            onChange={(_, val) => setValue("smtp_port", val)}
          >
            <NumberInputField {...register("smtp_port", { valueAsNumber: true })} />
          </NumberInput>
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.username")}</FormLabel>
          <Input
            {...register("smtp_username")}
            placeholder="user@example.com"
          />
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.password")}</FormLabel>
          <InputGroup>
            <Input
              {...register("smtp_password")}
              type={showPassword ? "text" : "password"}
              placeholder="********"
            />
            <InputRightElement width="4.5rem">
              <Button
                h="1.75rem"
                size="sm"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? t("common.hide") : t("common.show")}
              </Button>
            </InputRightElement>
          </InputGroup>
        </FormControl>

        <FormControl mb={4} display="flex" alignItems="center">
          <FormLabel color={color} mb="0">
            {t("settings.smtp.useTls")}
          </FormLabel>
          <Switch
            {...register("smtp_use_tls")}
            isChecked={useTls ?? true}
            onChange={(e) => setValue("smtp_use_tls", e.target.checked)}
          />
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.fromEmail")}</FormLabel>
          <Input
            {...register("smtp_from_email")}
            type="email"
            placeholder="noreply@example.com"
          />
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.smtp.fromName")}</FormLabel>
          <Input
            {...register("smtp_from_name")}
            placeholder={t("settings.smtp.fromNamePlaceholder")}
          />
        </FormControl>

        <Flex mt={6} gap={3}>
          <Button
            variant="primary"
            type="submit"
            isLoading={isSubmitting || updateMutation.isPending}
            isDisabled={!isDirty}
          >
            {t("common.save")}
          </Button>
          <Button
            variant="outline"
            onClick={() => testMutation.mutate()}
            isLoading={testMutation.isPending}
          >
            {t("settings.smtp.testConnection")}
          </Button>
        </Flex>
      </Box>
    </Container>
  )
}

export default SmtpSettings
