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
import { useTranslation } from "react-i18next"

import {
  type ApiError,
  type ItemPublic,
  type RecipeCreate,
  ItemsService,
  RecipesService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddRecipeProps {
  isOpen: boolean
  onClose: () => void
}

const AddRecipe = ({ isOpen, onClose }: AddRecipeProps) => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  const { data: items } = useQuery({
    queryKey: ["items"],
    queryFn: () => ItemsService.readItems({ skip: 0, limit: 999 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RecipeCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: "",
      name: "",
      description: "",
      output_item_id: "",
      output_quantity: 1,
      unit: "бр.",
      version: "1.0",
      is_active: true,
      production_cost: 0,
      notes: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: RecipeCreate) =>
      RecipesService.createRecipeEndpoint({ requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("recipes.messages.created"), "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] })
    },
  })

  const onSubmit: SubmitHandler<RecipeCreate> = (data) => {
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
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)} maxW="700px">
        <ModalHeader>{t("recipes.addRecipe")}</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isRequired isInvalid={!!errors.code}>
              <FormLabel>{t("recipes.code")}</FormLabel>
              <Input
                {...register("code", {
                  required: t("errors.requiredField"),
                  maxLength: { value: 50, message: t("errors.maxLength", { max: 50 }) },
                })}
                placeholder="RCP-001"
              />
              {errors.code && (
                <FormErrorMessage>{errors.code.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel>{t("recipes.name")}</FormLabel>
              <Input
                {...register("name", {
                  required: t("errors.requiredField"),
                  maxLength: { value: 120, message: t("errors.maxLength", { max: 120 }) },
                })}
                placeholder={t("recipes.namePlaceholder")}
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.output_item_id}>
              <FormLabel>{t("recipes.outputItem")}</FormLabel>
              <Select
                {...register("output_item_id", {
                  required: t("errors.requiredField"),
                })}
                placeholder={t("recipes.selectOutputItem")}
              >
                {items?.data?.map((item: ItemPublic) => (
                  <option key={item.id} value={item.id}>
                    {item.title}
                  </option>
                ))}
              </Select>
              {errors.output_item_id && (
                <FormErrorMessage>{errors.output_item_id.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isRequired isInvalid={!!errors.output_quantity}>
              <FormLabel>{t("recipes.outputQuantity")}</FormLabel>
              <Input
                type="number"
                step="0.0001"
                {...register("output_quantity", {
                  required: t("errors.requiredField"),
                  valueAsNumber: true,
                  min: { value: 0.0001, message: t("errors.minValue", { min: 0.0001 }) },
                })}
                placeholder="1"
              />
              {errors.output_quantity && (
                <FormErrorMessage>{errors.output_quantity.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl>
              <FormLabel>{t("recipes.unit")}</FormLabel>
              <Input
                {...register("unit")}
                placeholder="бр."
              />
            </FormControl>

            <FormControl>
              <FormLabel>{t("recipes.version")}</FormLabel>
              <Input
                {...register("version")}
                placeholder="1.0"
              />
            </FormControl>

            <FormControl>
              <FormLabel>{t("recipes.productionCost")}</FormLabel>
              <Input
                type="number"
                step="0.01"
                {...register("production_cost", { valueAsNumber: true })}
                placeholder="0.00"
              />
            </FormControl>
          </SimpleGrid>

          <FormControl mt={4}>
            <FormLabel>{t("fields.description")}</FormLabel>
            <Textarea
              {...register("description")}
              placeholder={t("recipes.descriptionPlaceholder")}
              rows={2}
            />
          </FormControl>

          <FormControl mt={4}>
            <FormLabel>{t("fields.notes")}</FormLabel>
            <Textarea
              {...register("notes")}
              placeholder={t("recipes.notesPlaceholder")}
              rows={2}
            />
          </FormControl>

          <FormControl mt={4}>
            <Checkbox {...register("is_active")} defaultChecked>
              {t("recipes.isActive")}
            </Checkbox>
          </FormControl>
        </ModalBody>

        <ModalFooter gap={3}>
          <Button variant="primary" type="submit" isLoading={isSubmitting}>
            {t("common.save")}
          </Button>
          <Button onClick={onClose}>{t("common.cancel")}</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default AddRecipe
