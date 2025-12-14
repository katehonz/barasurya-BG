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
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type ItemCategoryPublic,
  type ItemCreate,
  type ItemUnitPublic,
  ItemCategoriesService,
  ItemsService,
  ItemUnitsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddItemProps {
  isOpen: boolean
  onClose: () => void
}

const AddItem = ({ isOpen, onClose }: AddItemProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  const { data: item_categories } = useQuery({
    queryKey: ["item_categories"],
    queryFn: () => ItemCategoriesService.readItemCategories({ skip: 0, limit: 999 }),
  })

  const { data: item_units } = useQuery({
    queryKey: ["item_units"],
    queryFn: () => ItemUnitsService.readItemUnits({ skip: 0, limit: 999 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ItemCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      description: "",
      price_purchase: null,
      price_sell: null,
      stock_minimum: 0,
      is_active: true,
      item_category_id: "",
      item_unit_id: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ItemCreate) =>
      ItemsService.createItem({ requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Артикулът е създаден успешно.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit: SubmitHandler<ItemCreate> = (data) => {
    mutation.mutate(data)
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
        <ModalHeader>Добавяне на артикул</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isRequired isInvalid={!!errors.title}>
              <FormLabel>Наименование</FormLabel>
              <Input
                {...register("title", {
                  required: "Наименованието е задължително",
                })}
                placeholder="Продукт ABC"
              />
              {errors.title && (
                <FormErrorMessage>{errors.title.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.item_category_id}>
              <FormLabel>Категория</FormLabel>
              <Select
                {...register("item_category_id", {
                  required: "Категорията е задължителна",
                })}
                placeholder="Изберете категория"
              >
                {item_categories?.data?.map((cat: ItemCategoryPublic) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </Select>
              {errors.item_category_id && (
                <FormErrorMessage>{errors.item_category_id.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.item_unit_id}>
              <FormLabel>Мерна единица</FormLabel>
              <Select
                {...register("item_unit_id", {
                  required: "Мерната единица е задължителна",
                })}
                placeholder="Изберете единица"
              >
                {item_units?.data?.map((unit: ItemUnitPublic) => (
                  <option key={unit.id} value={unit.id}>
                    {unit.name}
                  </option>
                ))}
              </Select>
              {errors.item_unit_id && (
                <FormErrorMessage>{errors.item_unit_id.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl>
              <FormLabel>Покупна цена (лв.)</FormLabel>
              <Input
                type="number"
                step="0.01"
                {...register("price_purchase", { valueAsNumber: true })}
                placeholder="0.00"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Продажна цена (лв.)</FormLabel>
              <Input
                type="number"
                step="0.01"
                {...register("price_sell", { valueAsNumber: true })}
                placeholder="0.00"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Минимална наличност</FormLabel>
              <Input
                type="number"
                {...register("stock_minimum", { valueAsNumber: true })}
                placeholder="0"
              />
            </FormControl>
          </SimpleGrid>

          <FormControl mt={4}>
            <FormLabel>Описание</FormLabel>
            <Textarea
              {...register("description")}
              placeholder="Описание на артикула..."
              rows={2}
            />
          </FormControl>

          <FormControl mt={4}>
            <Checkbox {...register("is_active")} defaultChecked>
              Активен
            </Checkbox>
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

export default AddItem
