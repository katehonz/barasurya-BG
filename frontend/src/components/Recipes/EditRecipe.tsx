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
  SimpleGrid,
  Textarea,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"

import {
  type ApiError,
  type RecipePublic,
  type RecipeUpdate,
  RecipesService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface EditRecipeProps {
  recipe: RecipePublic
  isOpen: boolean
  onClose: () => void
}

const EditRecipe = ({ recipe, isOpen, onClose }: EditRecipeProps) => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<RecipeUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: recipe.code,
      name: recipe.name,
      description: recipe.description || "",
      output_quantity: recipe.output_quantity,
      unit: recipe.unit,
      version: recipe.version,
      is_active: recipe.is_active,
      production_cost: recipe.production_cost,
      notes: recipe.notes || "",
    },
  })

  useEffect(() => {
    if (isOpen) {
      reset({
        code: recipe.code,
        name: recipe.name,
        description: recipe.description || "",
        output_quantity: recipe.output_quantity,
        unit: recipe.unit,
        version: recipe.version,
        is_active: recipe.is_active,
        production_cost: recipe.production_cost,
        notes: recipe.notes || "",
      })
    }
  }, [recipe, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: RecipeUpdate) =>
      RecipesService.updateRecipeEndpoint({ recipeId: recipe.id, requestBody: data }),
    onSuccess: () => {
      showToast(t("common.success"), t("recipes.messages.updated"), "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] })
    },
  })

  const onSubmit: SubmitHandler<RecipeUpdate> = async (data) => {
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
      <ModalContent as="form" onSubmit={handleSubmit(onSubmit)} maxW="700px">
        <ModalHeader>{t("recipes.editRecipe")}</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl isInvalid={!!errors.code}>
              <FormLabel>{t("recipes.code")}</FormLabel>
              <Input
                {...register("code", {
                  maxLength: { value: 50, message: t("errors.maxLength", { max: 50 }) },
                })}
                placeholder="RCP-001"
              />
              {errors.code && (
                <FormErrorMessage>{errors.code.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isInvalid={!!errors.name}>
              <FormLabel>{t("recipes.name")}</FormLabel>
              <Input
                {...register("name", {
                  maxLength: { value: 120, message: t("errors.maxLength", { max: 120 }) },
                })}
                placeholder={t("recipes.namePlaceholder")}
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl isInvalid={!!errors.output_quantity}>
              <FormLabel>{t("recipes.outputQuantity")}</FormLabel>
              <Input
                type="number"
                step="0.0001"
                {...register("output_quantity", {
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
            <Checkbox {...register("is_active")}>
              {t("recipes.isActive")}
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
            {t("common.save")}
          </Button>
          <Button onClick={onCancel}>{t("common.cancel")}</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default EditRecipe
