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
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type PurchasePublic,
  type PurchaseUpdate,
  PurchasesService,
  SuppliersService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"
import { useEffect } from "react"

interface EditPurchaseProps {
  purchase: PurchasePublic
  isOpen: boolean
  onClose: () => void
}

const EditPurchase = ({ purchase, isOpen, onClose }: EditPurchaseProps) => {
  const { data: suppliers } = useQuery({
    queryKey: ["suppliers"],
    queryFn: () =>
      SuppliersService.readSuppliers({ skip: 0, limit: 999 }),
  })
  const { data: stores } = useQuery({
    queryKey: ["stores"],
    queryFn: () =>
      SuppliersService.readSuppliers({ skip: 0, limit: 999 }),
  })

  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<PurchaseUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: purchase,
  })

  useEffect(() => {
    if (isOpen) {
      reset(purchase)
    }
  }, [purchase, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: PurchaseUpdate) =>
      PurchasesService.updatePurchase({ id: purchase.id, requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Purchase updated successfully.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["purchases"] })
    },
  })

  const onSubmit: SubmitHandler<PurchaseUpdate> = async (data) => {
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
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Edit Purchase</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.date_purchase}>
              <FormLabel htmlFor="date_purchase">Date Purchase</FormLabel>
              <Input
                id="date_purchase"
                {...register("date_purchase", {
                  required: "Name is required",
                })}
                type="date"
              />
              {errors.date_purchase && (
                <FormErrorMessage>{errors.date_purchase.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="amount">Amount</FormLabel>
              <Input
                id="amount"
                {...register("amount")}
                placeholder="1000"
                type="number"
              />
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
            <FormControl isRequired isInvalid={!!errors.supplier_id} mt={4}>
              <FormLabel htmlFor="supplier_id">Supplier</FormLabel>
              <Select
                id="supplier_id"
                {...register("supplier_id", {
                  required: "Supplier of purchase is required."
                })}
                placeholder="Select the supplier">
                {suppliers?.data?.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name}
                  </option>
                ))}
              </Select>
              {errors.supplier_id && (
                <FormErrorMessage>{errors.supplier_id.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl isRequired isInvalid={!!errors.store_id} mt={4}>
              <FormLabel htmlFor="store_id">Store</FormLabel>
              <Select
                id="store_id"
                {...register("store_id", {
                  required: "Store of purchase is required."
                })}
                placeholder="Select the store">
                {stores?.data?.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name}
                  </option>
                ))}
              </Select>
              {errors.store_id && (
                <FormErrorMessage>{errors.store_id.message}</FormErrorMessage>
              )}
            </FormControl>
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

export default EditPurchase
