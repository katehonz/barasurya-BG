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
  Text,
  Badge,
} from "@chakra-ui/react"
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useEffect } from "react"

import {
  type ApiError,
  type ItemCategoryPublic,
  type ItemPublic,
  type ItemUnitPublic,
  type ItemUpdate,
  ItemsService,
  ItemCategoriesService,
  ItemUnitsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface EditItemProps {
  item: ItemPublic
  isOpen: boolean
  onClose: () => void
}

const EditItem = ({ item, isOpen, onClose }: EditItemProps) => {
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
    formState: { isSubmitting, errors, isDirty },
  } = useForm<ItemUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: item.title,
      description: item.description || "",
      price_purchase: item.price_purchase,
      price_sell: item.price_sell,
      stock_minimum: item.stock_minimum,
      is_active: item.is_active,
      item_category_id: item.item_category_id,
      item_unit_id: item.item_unit_id,
    },
  })

  useEffect(() => {
    if (isOpen) {
      reset({
        title: item.title,
        description: item.description || "",
        price_purchase: item.price_purchase,
        price_sell: item.price_sell,
        stock_minimum: item.stock_minimum,
        is_active: item.is_active,
        item_category_id: item.item_category_id,
        item_unit_id: item.item_unit_id,
      })
    }
  }, [item, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: ItemUpdate) =>
      ItemsService.updateItem({ id: item.id, requestBody: data }),
    onSuccess: () => {
      showToast("Успех!", "Артикулът е обновен успешно.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit: SubmitHandler<ItemUpdate> = async (data) => {
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
        <ModalHeader>Редактиране на артикул</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          {/* Show current stock (read-only) */}
          <FormControl mb={4}>
            <FormLabel>Текуща наличност</FormLabel>
            <Text fontSize="lg" fontWeight="bold">
              {item.stock} {item.item_unit_name}
              {item.stock <= (item.stock_minimum || 0) && (
                <Badge colorScheme="red" ml={2}>Ниска наличност</Badge>
              )}
            </Text>
          </FormControl>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isInvalid={!!errors.title}>
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

            <FormControl isInvalid={!!errors.item_category_id}>
              <FormLabel>Категория</FormLabel>
              <Select
                {...register("item_category_id")}
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

            <FormControl isInvalid={!!errors.item_unit_id}>
              <FormLabel>Мерна единица</FormLabel>
              <Select
                {...register("item_unit_id")}
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
            <Checkbox {...register("is_active")}>
              Активен
            </Checkbox>
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

export default EditItem
