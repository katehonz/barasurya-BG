import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  SimpleGrid,
  Textarea,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  AssetsService,
  AccountsService,
  ContraagentsService,
  type AccountPublic,
  type ApiError,
  type AssetCreate,
  type ContraagentPublic,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddAssetProps {
  isOpen: boolean
  onClose: () => void
}

const AddAsset = ({ isOpen, onClose }: AddAssetProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  const { data: accounts } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts({ limit: 1000 }),
  })

  const { data: contraagents } = useQuery({
    queryKey: ["contraagents"],
    queryFn: () => ContraagentsService.readContraagents({ limit: 1000 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AssetCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: "",
      name: "",
      acquisition_date: new Date().toISOString().split("T")[0],
      acquisition_cost: 0,
      useful_life_months: 60,
      depreciation_method: "straight_line",
      salvage_value: 0,
      category: "",
      inventory_number: "",
      serial_number: "",
      location: "",
      responsible_person: "",
      tax_category: "",
      tax_depreciation_rate: null,
      accounting_depreciation_rate: null,
      accounting_account_id: null,
      expense_account_id: null,
      accumulated_depreciation_account_id: null,
      contraagent_id: null,
      notes: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AssetCreate) =>
      AssetsService.createAsset({ requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Активът е създаден успешно.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] })
    },
  })

  const onSubmit: SubmitHandler<AssetCreate> = (data) => {
    // Convert empty strings to null for optional UUID fields
    const cleanedData = {
      ...data,
      contraagent_id: data.contraagent_id || null,
      accounting_account_id: data.accounting_account_id || null,
      expense_account_id: data.expense_account_id || null,
      accumulated_depreciation_account_id: data.accumulated_depreciation_account_id || null,
    }
    mutation.mutate(cleanedData)
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="xl"
      isCentered
      scrollBehavior="inside"
    >
      <ModalOverlay />
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)} maxW="800px">
        <ModalHeader>Добавяне на ДМА</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <Tabs>
            <TabList>
              <Tab>Основни данни</Tab>
              <Tab>Амортизация</Tab>
              <Tab>Счетоводство</Tab>
              <Tab>Допълнителни</Tab>
            </TabList>

            <TabPanels>
              {/* Основни данни */}
              <TabPanel>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired isInvalid={!!errors.code}>
                    <FormLabel>Код</FormLabel>
                    <Input
                      {...register("code", { required: "Кодът е задължителен" })}
                      placeholder="ДМА-001"
                    />
                    {errors.code && (
                      <FormErrorMessage>{errors.code.message}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isRequired isInvalid={!!errors.name}>
                    <FormLabel>Наименование</FormLabel>
                    <Input
                      {...register("name", { required: "Наименованието е задължително" })}
                      placeholder="Компютър HP"
                    />
                    {errors.name && (
                      <FormErrorMessage>{errors.name.message}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl>
                    <FormLabel>Категория</FormLabel>
                    <Select {...register("category")} placeholder="Изберете категория">
                      <option value="computers">Компютри и периферия</option>
                      <option value="furniture">Мебели</option>
                      <option value="vehicles">Транспортни средства</option>
                      <option value="machinery">Машини и оборудване</option>
                      <option value="buildings">Сгради</option>
                      <option value="land">Земя</option>
                      <option value="software">Софтуер</option>
                      <option value="other">Други</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Инвентарен номер</FormLabel>
                    <Input
                      {...register("inventory_number")}
                      placeholder="INV-2024-001"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Сериен номер</FormLabel>
                    <Input
                      {...register("serial_number")}
                      placeholder="SN123456789"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Местоположение</FormLabel>
                    <Input
                      {...register("location")}
                      placeholder="Офис 101"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>МОЛ</FormLabel>
                    <Input
                      {...register("responsible_person")}
                      placeholder="Иван Иванов"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Доставчик</FormLabel>
                    <Select {...register("contraagent_id")} placeholder="Изберете доставчик">
                      {contraagents?.data
                        .filter((c: ContraagentPublic) => c.is_supplier)
                        .map((contraagent: ContraagentPublic) => (
                          <option key={contraagent.id} value={contraagent.id}>
                            {contraagent.name}
                          </option>
                        ))}
                    </Select>
                  </FormControl>
                </SimpleGrid>
              </TabPanel>

              {/* Амортизация */}
              <TabPanel>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired isInvalid={!!errors.acquisition_date}>
                    <FormLabel>Дата на придобиване</FormLabel>
                    <Input
                      type="date"
                      {...register("acquisition_date", {
                        required: "Датата е задължителна",
                      })}
                    />
                    {errors.acquisition_date && (
                      <FormErrorMessage>{errors.acquisition_date.message}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isRequired isInvalid={!!errors.acquisition_cost}>
                    <FormLabel>Първоначална стойност (лв.)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      {...register("acquisition_cost", {
                        required: "Стойността е задължителна",
                        valueAsNumber: true,
                      })}
                      placeholder="0.00"
                    />
                    {errors.acquisition_cost && (
                      <FormErrorMessage>{errors.acquisition_cost.message}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isRequired isInvalid={!!errors.useful_life_months}>
                    <FormLabel>Полезен живот (месеци)</FormLabel>
                    <Input
                      type="number"
                      {...register("useful_life_months", {
                        required: "Полезният живот е задължителен",
                        valueAsNumber: true,
                        min: { value: 1, message: "Минимум 1 месец" },
                      })}
                      placeholder="60"
                    />
                    {errors.useful_life_months && (
                      <FormErrorMessage>{errors.useful_life_months.message}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl>
                    <FormLabel>Метод на амортизация</FormLabel>
                    <Select {...register("depreciation_method")}>
                      <option value="straight_line">Линеен</option>
                      <option value="declining_balance">Намаляващо салдо</option>
                      <option value="sum_of_years">Сума на числата</option>
                      <option value="units_of_production">Производствен</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Остатъчна стойност (лв.)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      {...register("salvage_value", { valueAsNumber: true })}
                      placeholder="0.00"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Данъчна категория</FormLabel>
                    <Select {...register("tax_category")} placeholder="Изберете категория">
                      <option value="I">I - Масивни сгради (4%)</option>
                      <option value="II">II - Машини и оборудване (30%)</option>
                      <option value="III">III - Транспортни средства (10%)</option>
                      <option value="IV">IV - Компютри и софтуер (50%)</option>
                      <option value="V">V - Други (15%)</option>
                      <option value="VI">VI - Дълготрайни нематериални активи (33.33%)</option>
                      <option value="VII">VII - Дълготрайни биологични активи (15%)</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Данъчна норма (%)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      {...register("tax_depreciation_rate", { valueAsNumber: true })}
                      placeholder="25.00"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Счетоводна норма (%)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      {...register("accounting_depreciation_rate", { valueAsNumber: true })}
                      placeholder="20.00"
                    />
                  </FormControl>
                </SimpleGrid>
              </TabPanel>

              {/* Счетоводство */}
              <TabPanel>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl>
                    <FormLabel>Сметка на актива</FormLabel>
                    <Select {...register("accounting_account_id")} placeholder="Изберете сметка">
                      {accounts?.data
                        .filter((a: AccountPublic) => a.code.startsWith("20") || a.code.startsWith("21"))
                        .map((account: AccountPublic) => (
                          <option key={account.id} value={account.id}>
                            {account.code} - {account.name}
                          </option>
                        ))}
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Сметка за амортизационни разходи</FormLabel>
                    <Select {...register("expense_account_id")} placeholder="Изберете сметка">
                      {accounts?.data
                        .filter((a: AccountPublic) => a.code.startsWith("60"))
                        .map((account: AccountPublic) => (
                          <option key={account.id} value={account.id}>
                            {account.code} - {account.name}
                          </option>
                        ))}
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Сметка за натрупана амортизация</FormLabel>
                    <Select {...register("accumulated_depreciation_account_id")} placeholder="Изберете сметка">
                      {accounts?.data
                        .filter((a: AccountPublic) => a.code.startsWith("24"))
                        .map((account: AccountPublic) => (
                          <option key={account.id} value={account.id}>
                            {account.code} - {account.name}
                          </option>
                        ))}
                    </Select>
                  </FormControl>

                </SimpleGrid>
              </TabPanel>

              {/* Допълнителни */}
              <TabPanel>
                <FormControl>
                  <FormLabel>Бележки</FormLabel>
                  <Textarea
                    {...register("notes")}
                    placeholder="Допълнителна информация за актива..."
                    rows={4}
                  />
                </FormControl>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>

        <ModalFooter gap={3}>
          <Button variant="primary" type="submit" isLoading={isSubmitting}>
            Запази
          </Button>
          <Button onClick={onClose}>Отказ</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default AddAsset
