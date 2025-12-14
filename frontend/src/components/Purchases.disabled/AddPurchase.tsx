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
import { StoresService, SuppliersService } from "../../client"

import { type ApiError, type PurchaseCreate, PurchasesService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddPurchaseProps {
  isOpen: boolean
  onClose: () => void
}

const AddPurchase = ({ isOpen, onClose }: AddPurchaseProps) => {
  const { data: suppliers } = useQuery({
    queryKey: ["suppliers"],
    queryFn: () =>
      SuppliersService.readSuppliers({ skip: 0, limit: 999 }),
  })
  const { data: stores } = useQuery({
    queryKey: ["stores"],
    queryFn: () =>
      StoresService.readStores({ skip: 0, limit: 999 }),
  })

  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PurchaseCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      date_purchase: "",
      amount: 0,
      description: "",
      supplier_id: "",
      store_id: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: PurchaseCreate) =>
      PurchasesService.createPurchase({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Purchase created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["purchases"] })
    },
  })

  const onSubmit: SubmitHandler<PurchaseCreate> = (data) => {
    mutation.mutate(data)
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
          <ModalHeader>Add Purchase</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.date_purchase}>
              <FormLabel htmlFor="date_purchase">Date Purchase</FormLabel>
              <Input
                id="date_purchase"
                type="date"
                placeholder="Select date purchase"
                {...register("date_purchase", {
                  required: "Date purchase is required.",
                })}
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

export default AddPurchase
