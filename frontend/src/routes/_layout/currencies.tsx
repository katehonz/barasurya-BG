import { useState } from "react"
import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  HStack,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useColorModeValue,
  useDisclosure,
  Badge,
  IconButton,
  Tooltip,
  Alert,
  AlertIcon,
  Spinner,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Switch,
  VStack,
} from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { FiPlus, FiEdit, FiTrash2, FiRefreshCw, FiDollarSign } from "react-icons/fi"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import type { CurrencyPublic, CurrencyCreate, CurrencyUpdate } from "../../client"
import { CurrenciesService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

export const Route = createFileRoute("/_layout/currencies")({
  component: Currencies,
})

interface CurrencyFormData {
  code: string
  name: string
  name_bg?: string
  symbol?: string
  decimal_places: number
  is_active: boolean
  is_base_currency: boolean
}

function AddCurrencyModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean
  onClose: () => void
}) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CurrencyFormData>({
    defaultValues: {
      decimal_places: 2,
      is_active: true,
      is_base_currency: false,
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: CurrencyCreate) => CurrenciesService.createCurrency({ requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("currencies.created"), "success")
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
      reset()
      onClose()
    },
    onError: (err: any) => {
      handleError(err, showToast)
    },
  })

  const onSubmit = (data: CurrencyFormData) => {
    createMutation.mutate(data as CurrencyCreate)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
        <ModalHeader>{t("currencies.addCurrency")}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl isRequired isInvalid={!!errors.code}>
              <FormLabel>{t("currencies.code")}</FormLabel>
              <Input
                {...register("code", { required: true, maxLength: 3 })}
                placeholder="BGN"
                maxLength={3}
                textTransform="uppercase"
              />
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel>{t("currencies.name")}</FormLabel>
              <Input {...register("name", { required: true })} placeholder="Bulgarian Lev" />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.nameBg")}</FormLabel>
              <Input {...register("name_bg")} placeholder="Български лев" />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.symbol")}</FormLabel>
              <Input {...register("symbol")} placeholder="лв." maxLength={5} />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.decimalPlaces")}</FormLabel>
              <Input
                type="number"
                {...register("decimal_places", { valueAsNumber: true })}
                defaultValue={2}
                min={0}
                max={6}
              />
            </FormControl>

            <HStack w="full" justify="space-between">
              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">{t("currencies.active")}</FormLabel>
                <Switch {...register("is_active")} defaultChecked />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">{t("currencies.baseCurrency")}</FormLabel>
                <Switch {...register("is_base_currency")} />
              </FormControl>
            </HStack>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button
            colorScheme="teal"
            type="submit"
            isLoading={isSubmitting || createMutation.isPending}
          >
            {t("common.create")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

function EditCurrencyModal({
  isOpen,
  onClose,
  currency,
}: {
  isOpen: boolean
  onClose: () => void
  currency: CurrencyPublic
}) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CurrencyFormData>({
    defaultValues: {
      code: currency.code,
      name: currency.name,
      name_bg: currency.name_bg || "",
      symbol: currency.symbol || "",
      decimal_places: currency.decimal_places,
      is_active: currency.is_active,
      is_base_currency: currency.is_base_currency,
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: CurrencyUpdate) =>
      CurrenciesService.updateCurrency({ id: currency.id, requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("currencies.updated"), "success")
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
      onClose()
    },
    onError: (err: any) => {
      handleError(err, showToast)
    },
  })

  const onSubmit = (data: CurrencyFormData) => {
    updateMutation.mutate(data as CurrencyUpdate)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
        <ModalHeader>{t("currencies.editCurrency")}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl isRequired isInvalid={!!errors.code}>
              <FormLabel>{t("currencies.code")}</FormLabel>
              <Input
                {...register("code", { required: true, maxLength: 3 })}
                placeholder="BGN"
                maxLength={3}
                textTransform="uppercase"
              />
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel>{t("currencies.name")}</FormLabel>
              <Input {...register("name", { required: true })} placeholder="Bulgarian Lev" />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.nameBg")}</FormLabel>
              <Input {...register("name_bg")} placeholder="Български лев" />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.symbol")}</FormLabel>
              <Input {...register("symbol")} placeholder="лв." maxLength={5} />
            </FormControl>

            <FormControl>
              <FormLabel>{t("currencies.decimalPlaces")}</FormLabel>
              <Input
                type="number"
                {...register("decimal_places", { valueAsNumber: true })}
                min={0}
                max={6}
              />
            </FormControl>

            <HStack w="full" justify="space-between">
              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">{t("currencies.active")}</FormLabel>
                <Switch {...register("is_active")} defaultChecked={currency.is_active} />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">{t("currencies.baseCurrency")}</FormLabel>
                <Switch {...register("is_base_currency")} defaultChecked={currency.is_base_currency} />
              </FormControl>
            </HStack>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button
            colorScheme="teal"
            type="submit"
            isLoading={isSubmitting || updateMutation.isPending}
          >
            {t("common.save")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

function Currencies() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    isOpen: isAddOpen,
    onOpen: onAddOpen,
    onClose: onAddClose,
  } = useDisclosure()
  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure()
  const [selectedCurrency, setSelectedCurrency] = useState<CurrencyPublic | null>(null)

  // Fetch currencies
  const {
    data: currenciesData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["currencies"],
    queryFn: () => CurrenciesService.readCurrencies({ skip: 0, limit: 100 }),
  })

  // Delete currency mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => CurrenciesService.deleteCurrency({ id }),
    onSuccess: () => {
      showToast(t("common.success"), t("currencies.deleted"), "success")
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
    },
    onError: (err: any) => {
      handleError(err, showToast)
    },
  })

  // Update ECB rates mutation
  const updateRatesMutation = useMutation({
    mutationFn: () => CurrenciesService.updateEcbRates(),
    onSuccess: (data: any) => {
      showToast(t("common.success"), data.message || t("currencies.ratesUpdated"), "success")
      queryClient.invalidateQueries({ queryKey: ["currencies"] })
      queryClient.invalidateQueries({ queryKey: ["exchange-rates"] })
    },
    onError: (err: any) => {
      handleError(err, showToast)
    },
  })

  const handleEdit = (currency: CurrencyPublic) => {
    setSelectedCurrency(currency)
    onEditOpen()
  }

  const handleDelete = (id: string, isBase: boolean | undefined) => {
    if (isBase) {
      showToast(t("common.error"), t("currencies.cannotDeleteBase"), "error")
      return
    }
    if (window.confirm(t("currencies.confirmDelete"))) {
      deleteMutation.mutate(id)
    }
  }

  const tableBg = useColorModeValue("white", "gray.800")
  const headerBg = useColorModeValue("gray.50", "gray.700")

  if (error) {
    return (
      <Container maxW="full">
        <Alert status="error">
          <AlertIcon />
          {t("currencies.loadError")}
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Box bg={tableBg} rounded="md" shadow="base" w="full" p={6} mb={6}>
        <Flex justify="space-between" align="center" mb={6}>
          <Heading size="lg">{t("currencies.title")}</Heading>
          <HStack>
            <Button
              leftIcon={<FiDollarSign />}
              onClick={() => updateRatesMutation.mutate()}
              isLoading={updateRatesMutation.isPending}
              variant="outline"
              colorScheme="blue"
            >
              {t("currencies.updateRates")}
            </Button>
            <Button
              leftIcon={<FiRefreshCw />}
              onClick={() => refetch()}
              isLoading={isLoading}
              variant="outline"
            >
              {t("common.refresh")}
            </Button>
            <Button leftIcon={<FiPlus />} onClick={onAddOpen} colorScheme="teal">
              {t("currencies.addCurrency")}
            </Button>
          </HStack>
        </Flex>

        {/* Results Summary */}
        {currenciesData && (
          <Text mb={4} color="gray.600">
            {t("currencies.showing", { count: currenciesData.data.length })}
          </Text>
        )}

        {/* Table */}
        {isLoading ? (
          <Flex justify="center" py={8}>
            <Spinner size="xl" />
          </Flex>
        ) : (
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead bg={headerBg}>
                <Tr>
                  <Th>{t("currencies.code")}</Th>
                  <Th>{t("currencies.name")}</Th>
                  <Th>{t("currencies.nameBg")}</Th>
                  <Th>{t("currencies.symbol")}</Th>
                  <Th>{t("currencies.decimalPlaces")}</Th>
                  <Th>{t("currencies.status")}</Th>
                  <Th>{t("common.actions")}</Th>
                </Tr>
              </Thead>
              <Tbody>
                {currenciesData?.data?.map((currency) => (
                  <Tr key={currency.id}>
                    <Td>
                      <HStack>
                        <Text fontWeight="bold" fontFamily="mono">
                          {currency.code}
                        </Text>
                        {currency.is_base_currency && (
                          <Badge colorScheme="purple" size="sm">
                            {t("currencies.base")}
                          </Badge>
                        )}
                      </HStack>
                    </Td>
                    <Td>{currency.name}</Td>
                    <Td>{currency.name_bg || "-"}</Td>
                    <Td>
                      <Text fontFamily="mono">{currency.symbol || "-"}</Text>
                    </Td>
                    <Td>{currency.decimal_places}</Td>
                    <Td>
                      <Badge colorScheme={currency.is_active ? "green" : "red"} size="sm">
                        {currency.is_active ? t("currencies.active") : t("currencies.inactive")}
                      </Badge>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Tooltip label={t("common.edit")}>
                          <IconButton
                            aria-label={t("common.edit")}
                            icon={<FiEdit />}
                            size="sm"
                            variant="ghost"
                            colorScheme="blue"
                            onClick={() => handleEdit(currency)}
                          />
                        </Tooltip>
                        <Tooltip
                          label={
                            currency.is_base_currency
                              ? t("currencies.cannotDeleteBase")
                              : t("common.delete")
                          }
                        >
                          <IconButton
                            aria-label={t("common.delete")}
                            icon={<FiTrash2 />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => handleDelete(currency.id, currency.is_base_currency)}
                            isDisabled={currency.is_base_currency}
                            isLoading={deleteMutation.isPending}
                          />
                        </Tooltip>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
      </Box>

      {/* Add Modal */}
      <AddCurrencyModal isOpen={isAddOpen} onClose={onAddClose} />

      {/* Edit Modal */}
      {selectedCurrency && (
        <EditCurrencyModal isOpen={isEditOpen} onClose={onEditClose} currency={selectedCurrency} />
      )}
    </Container>
  )
}
