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
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useEffect } from "react"

import {
  type ApiError,
  type AccountPublic,
  type AccountUpdate,
  AccountsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface EditAccountProps {
  account: AccountPublic
  isOpen: boolean
  onClose: () => void
}

const EditAccount = ({ account, isOpen, onClose }: EditAccountProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<AccountUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: account.code,
      name: account.name,
      description: account.description || "",
      account_type: account.account_type,
      is_debit_account: account.is_debit_account,
      is_active: account.is_active,
      opening_balance: account.opening_balance || 0,
    },
  })

  useEffect(() => {
    if (isOpen) {
      reset({
        code: account.code,
        name: account.name,
        description: account.description || "",
        account_type: account.account_type,
        is_debit_account: account.is_debit_account,
        is_active: account.is_active,
        opening_balance: account.opening_balance || 0,
      })
    }
  }, [account, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: AccountUpdate) =>
      AccountsService.updateAccount({ id: account.id, requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Сметката е обновена успешно.", "success")
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

  const onSubmit: SubmitHandler<AccountUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
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
        <ModalHeader>Редактиране на сметка</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isInvalid={!!errors.code}>
              <FormLabel>Код на сметката</FormLabel>
              <Input
                {...register("code", {
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

            <FormControl isInvalid={!!errors.name}>
              <FormLabel>Наименование</FormLabel>
              <Input
                {...register("name")}
                placeholder="Доставчици"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl>
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
              <FormLabel>Начално салдо (лв.)</FormLabel>
              <Input
                type="number"
                step="0.01"
                {...register("opening_balance", { valueAsNumber: true })}
                placeholder="0.00"
              />
            </FormControl>

            <FormControl display="flex" flexDirection="column" gap={2} pt={6}>
              <Checkbox {...register("is_debit_account")}>
                Дебитна сметка
              </Checkbox>
              <Checkbox {...register("is_active")}>
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
          <Button
            variant="primary"
            type="submit"
            isLoading={isSubmitting}
            isDisabled={!isDirty}
          >
            Запази
          </Button>
          <Button onClick={onCancel}>Отказ</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default EditAccount
