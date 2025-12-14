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
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type AssetPublic,
  type AssetUpdate,
  AssetsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface EditAssetProps {
  asset: AssetPublic
  isOpen: boolean
  onClose: () => void
}

const EditAsset = ({ asset, isOpen, onClose }: EditAssetProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<AssetUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: asset.name,
      description: asset.description || "",
      acquisition_date: asset.acquisition_date.toISOString().split("T")[0],
      acquisition_cost: asset.acquisition_cost,
      depreciation_method: asset.depreciation_method,
      useful_life: asset.useful_life,
      salvage_value: asset.salvage_value,
      status: asset.status,
      inventory_number: asset.inventory_number || "",
      serial_number: asset.serial_number || "",
      location: asset.location || "",
      responsible_person: asset.responsible_person || "",
    },
  })

  useEffect(() => {
    if (isOpen) {
      reset({
        name: asset.name,
        description: asset.description || "",
        acquisition_date: asset.acquisition_date.toISOString().split("T")[0],
        acquisition_cost: asset.acquisition_cost,
        depreciation_method: asset.depreciation_method,
        useful_life: asset.useful_life,
        salvage_value: asset.salvage_value,
        status: asset.status,
        inventory_number: asset.inventory_number || "",
        serial_number: asset.serial_number || "",
        location: asset.location || "",
        responsible_person: asset.responsible_person || "",
      })
    }
  }, [asset, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: AssetUpdate) =>
      AssetsService.updateAsset({ id: asset.id, requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Asset updated successfully.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] })
    },
  })

  const onSubmit: SubmitHandler<AssetUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "md", md: "lg" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Edit Asset</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("name", {
                  required: "Name is required",
                })}
                type="text"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="description">Description</FormLabel>
              <Input
                id="description"
                {...register("description")}
                placeholder="Description"
                type="text"
              />
            </FormControl>

            <FormControl mt={4} isRequired isInvalid={!!errors.acquisition_date}>
              <FormLabel htmlFor="acquisition_date">Acquisition Date</FormLabel>
              <Input
                id="acquisition_date"
                {...register("acquisition_date", {
                  required: "Acquisition date is required.",
                })}
                type="date"
              />
              {errors.acquisition_date && (
                <FormErrorMessage>{errors.acquisition_date.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl mt={4} isRequired isInvalid={!!errors.acquisition_cost}>
              <FormLabel htmlFor="acquisition_cost">Acquisition Cost</FormLabel>
              <Input
                id="acquisition_cost"
                {...register("acquisition_cost", {
                  required: "Acquisition cost is required.",
                  valueAsNumber: true,
                })}
                placeholder="0.00"
                type="number"
                step="0.01"
              />
              {errors.acquisition_cost && (
                <FormErrorMessage>{errors.acquisition_cost.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl mt={4} isRequired isInvalid={!!errors.useful_life}>
              <FormLabel htmlFor="useful_life">Useful Life (Years)</FormLabel>
              <Input
                id="useful_life"
                {...register("useful_life", {
                  required: "Useful life is required.",
                  valueAsNumber: true,
                })}
                placeholder="0"
                type="number"
              />
              {errors.useful_life && (
                <FormErrorMessage>{errors.useful_life.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="depreciation_method">Depreciation Method</FormLabel>
              <Select
                id="depreciation_method"
                {...register("depreciation_method")}
              >
                <option value="straight_line">Straight Line</option>
                <option value="double_declining_balance">Double Declining Balance</option>
              </Select>
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="salvage_value">Salvage Value</FormLabel>
              <Input
                id="salvage_value"
                {...register("salvage_value", {
                  valueAsNumber: true,
                })}
                placeholder="0.00"
                type="number"
                step="0.01"
              />
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="status">Status</FormLabel>
              <Select
                id="status"
                {...register("status")}
              >
                <option value="active">Active</option>
                <option value="disposed">Disposed</option>
              </Select>
            </FormControl>

            {/* Additional fields can be added here as needed */}
          </ModalBody>
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!isDirty}
            >
              Save
            </Button>
            <Button onClick={onCancel}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default EditAsset
