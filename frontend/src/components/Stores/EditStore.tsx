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
import { useEffect } from "react"

import {
  type ApiError,
  type StorePublic,
  type StoreUpdate,
  StoresService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface EditStoreProps {
  store: StorePublic
  isOpen: boolean
  onClose: () => void
}

const EditStore = ({ store, isOpen, onClose }: EditStoreProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<StoreUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: store.name,
      address: store.address || "",
      latitude: store.latitude,
      longitude: store.longitude,
    },
  })

  useEffect(() => {
    if (isOpen) {
      reset({
        name: store.name,
        address: store.address || "",
        latitude: store.latitude,
        longitude: store.longitude,
      })
    }
  }, [store, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: StoreUpdate) =>
      StoresService.updateStore({ id: store.id, requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Складът е обновен успешно.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["stores"] })
    },
  })

  const onSubmit: SubmitHandler<StoreUpdate> = async (data) => {
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
      size="md"
      isCentered
    >
      <ModalOverlay />
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
        <ModalHeader>Редактиране на склад</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <FormControl isInvalid={!!errors.name}>
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

export default EditStore
