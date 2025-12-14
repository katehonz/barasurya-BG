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
  SimpleGrid,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, type StoreCreate, StoresService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddStoreProps {
  isOpen: boolean
  onClose: () => void
}

const AddStore = ({ isOpen, onClose }: AddStoreProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<StoreCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      address: "",
      latitude: null,
      longitude: null,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: StoreCreate) =>
      StoresService.createStore({ requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Складът е създаден успешно.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["stores"] })
    },
  })

  const onSubmit: SubmitHandler<StoreCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      isCentered
    >
      <ModalOverlay />
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
        <ModalHeader>Добавяне на склад</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <FormControl isRequired isInvalid={!!errors.name}>
            <FormLabel>Наименование</FormLabel>
            <Input
              {...register("name", {
                required: "Наименованието е задължително",
              })}
              placeholder="Централен склад"
            />
            {errors.name && (
              <FormErrorMessage>{errors.name.message}</FormErrorMessage>
            )}
          </FormControl>

          <FormControl mt={4}>
            <FormLabel>Адрес</FormLabel>
            <Input
              {...register("address")}
              placeholder="ул. Примерна 1, София"
            />
          </FormControl>

          <SimpleGrid columns={2} spacing={4} mt={4}>
            <FormControl>
              <FormLabel>Ширина (lat)</FormLabel>
              <Input
                type="number"
                step="any"
                {...register("latitude", { valueAsNumber: true })}
                placeholder="42.6977"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Дължина (lng)</FormLabel>
              <Input
                type="number"
                step="any"
                {...register("longitude", { valueAsNumber: true })}
                placeholder="23.3219"
              />
            </FormControl>
          </SimpleGrid>
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

export default AddStore
