import {
  Button,
  Checkbox,
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
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type AccountCreate,
  type AccountPublic,
  type ApiError,
  AccountsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddAccountProps {
  isOpen: boolean
  onClose: () => void
}

const AddAccount = ({ isOpen, onClose }: AddAccountProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  // Fetch accounts for parent selection
  const { data: accounts } = useQuery({
    queryKey: ["accounts-all"],
    queryFn: () => AccountsService.readAccounts({ limit: 1000 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AccountCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: "",
      name: "",
      description: "",
      account_type: "asset",
      is_debit_account: true,
      is_active: true,
      opening_balance: 0,
      parent_id: null,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AccountCreate) =>
      AccountsService.createAccount({ requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Сметката е създадена успешно.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
      queryClient.invalidateQueries({ queryKey: ["accounts-all"] })
    },
  })

  const onSubmit: SubmitHandler<AccountCreate> = (data) => {
    const cleanedData = {
      ...data,
      parent_id: data.parent_id || null,
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
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)} maxW="600px">
        <ModalHeader>Добавяне на сметка</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isRequired isInvalid={!!errors.code}>
              <FormLabel>Код на сметката</FormLabel>
              <Input
                {...register("code", {
                  required: "Кодът е задължителен",
                  pattern: {
                    value: /^\d{3,4}$/,
                    message: "Кодът трябва да е 3-4 цифри",
                  },
                })}
                placeholder="401"
              />
              {errors.code && (
                <FormErrorMessage>{errors.code.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel>Наименование</FormLabel>
              <Input
                {...register("name", {
                  required: "Наименованието е задължително",
                })}
                placeholder="Доставчици"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Тип сметка</FormLabel>
              <Select {...register("account_type")}>
                <option value="asset">Актив</option>
                <option value="liability">Пасив</option>
                <option value="equity">Собствен капитал</option>
                <option value="revenue">Приход</option>
                <option value="expense">Разход</option>
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>Родителска сметка</FormLabel>
              <Select {...register("parent_id")} placeholder="Без родител">
                {accounts?.data.map((account: AccountPublic) => (
                  <option key={account.id} value={account.id}>
                    {account.code} - {account.name}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>Начално салдо (лв.)</FormLabel>
              <Input
                type="number"
                step="0.01"
                {...register("opening_balance", { valueAsNumber: true })}
                placeholder="0.00"
              />
            </FormControl>

            <FormControl display="flex" flexDirection="column" gap={2} pt={6}>
              <Checkbox {...register("is_debit_account")} defaultChecked>
                Дебитна сметка
              </Checkbox>
              <Checkbox {...register("is_active")} defaultChecked>
                Активна
              </Checkbox>
            </FormControl>
          </SimpleGrid>

          <FormControl mt={4}>
            <FormLabel>Описание</FormLabel>
            <Textarea
              {...register("description")}
              placeholder="Описание на сметката..."
              rows={2}
            />
          </FormControl>
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

export default AddAccount
