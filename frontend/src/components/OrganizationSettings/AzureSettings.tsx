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
  Text,
  useColorModeValue,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import {
  type ApiError,
  type AzureSettingsUpdate,
  OrganizationSettingsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

const AzureSettings = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const color = useColorModeValue("inherit", "ui.light")
  const showToast = useCustomToast()
  const [showApiKey, setShowApiKey] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ["organizationSettings"],
    queryFn: () => OrganizationSettingsService.getSettings(),
  })

  const {
    register,
    handleSubmit,
    formState: { isSubmitting, isDirty },
  } = useForm<AzureSettingsUpdate>({
    mode: "onBlur",
    values: settings ? {
      azure_endpoint: settings.azure_endpoint,
      azure_api_key: settings.azure_api_key,
      azure_model_id: settings.azure_model_id,
    } : undefined,
  })

  const updateMutation = useMutation({
    mutationFn: (data: AzureSettingsUpdate) =>
      OrganizationSettingsService.updateAzureSettings({ requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("settings.azure.saved"), "success")
      queryClient.invalidateQueries({ queryKey: ["organizationSettings"] })
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
  })

  const onSubmit: SubmitHandler<AzureSettingsUpdate> = async (data) => {
    updateMutation.mutate(data)
  }

  if (isLoading) {
    return <Text>{t("common.loading")}</Text>
  }

  return (
    <Container maxW="full">
      <Heading size="sm" py={4}>
        {t("settings.azure.title")}
      </Heading>
      <Text color="gray.500" mb={4}>
        {t("settings.azure.description")}
      </Text>
      <Box
        w={{ sm: "full", md: "50%" }}
        as="form"
        onSubmit={handleSubmit(onSubmit)}
      >
        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.azure.endpoint")}</FormLabel>
          <Input
            {...register("azure_endpoint")}
            placeholder="https://your-resource.cognitiveservices.azure.com/"
          />
          <Text fontSize="sm" color="gray.500" mt={1}>
            {t("settings.azure.endpointHelp")}
          </Text>
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.azure.apiKey")}</FormLabel>
          <InputGroup>
            <Input
              {...register("azure_api_key")}
              type={showApiKey ? "text" : "password"}
              placeholder="********"
            />
            <InputRightElement width="4.5rem">
              <Button
                h="1.75rem"
                size="sm"
                onClick={() => setShowApiKey(!showApiKey)}
              >
                {showApiKey ? t("common.hide") : t("common.show")}
              </Button>
            </InputRightElement>
          </InputGroup>
          <Text fontSize="sm" color="gray.500" mt={1}>
            {t("settings.azure.apiKeyHelp")}
          </Text>
        </FormControl>

        <FormControl mb={4}>
          <FormLabel color={color}>{t("settings.azure.modelId")}</FormLabel>
          <Input
            {...register("azure_model_id")}
            placeholder="prebuilt-invoice"
          />
          <Text fontSize="sm" color="gray.500" mt={1}>
            {t("settings.azure.modelIdHelp")}
          </Text>
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
        </Flex>
      </Box>
    </Container>
  )
}

export default AzureSettings
