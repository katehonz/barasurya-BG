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
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  AssetsService,
  type ApiError,
  type AssetCreate,
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
      description: "",
      acquisition_date: new Date().toISOString().split("T")[0], // Default to today
      acquisition_cost: 0,
      depreciation_method: "straight_line",
      useful_life: 0,
      salvage_value: 0,
      status: "active",
      inventory_number: "",
      serial_number: "",
      location: "",
      responsible_person: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AssetCreate) =>
      AssetsService.createAsset({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Asset created successfully.", "success")
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
    mutation.mutate(data)
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
          <ModalHeader>Add Asset</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.code}>
              <FormLabel htmlFor="code">Code</FormLabel>
              <Input
                id="code"
                {...register("code", {
                  required: "Code is required.",
                })}
                placeholder="Unique asset code"
                type="text"
              />
              {errors.code && (
                <FormErrorMessage>{errors.code.message}</FormErrorMessage>
              )}
            </FormControl>

            <FormControl mt={4} isRequired isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("name", {
                  required: "Name is required.",
                })}
                placeholder="Asset name"
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
            {/* 
            <FormControl mt={4}>
              <FormLabel htmlFor="inventory_number">Inventory Number</FormLabel>
              <Input
                id="inventory_number"
                {...register("inventory_number")}
                placeholder="Inventory Number"
                type="text"
              />
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="serial_number">Serial Number</FormLabel>
              <Input
                id="serial_number"
                {...register("serial_number")}
                placeholder="Serial Number"
                type="text"
              />
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="location">Location</FormLabel>
              <Input
                id="location"
                {...register("location")}
                placeholder="Location"
                type="text"
              />
            </FormControl>

            <FormControl mt={4}>
              <FormLabel htmlFor="responsible_person">Responsible Person</FormLabel>
              <Input
                id="responsible_person"
                {...register("responsible_person")}
                placeholder="Responsible Person"
                type="text"
              />
            </FormControl>
            */}
          </ModalBody>

          <ModalFooter gap={3}>
            <Button variant="primary" type="submit" isLoading={isSubmitting}>
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddAsset
