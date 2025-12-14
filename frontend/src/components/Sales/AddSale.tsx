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
import { StoresService, CustomersService } from "../../client"

import { type ApiError, type SaleCreate, SalesService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddSaleProps {
  isOpen: boolean
  onClose: () => void
}

const AddSale = ({ isOpen, onClose }: AddSaleProps) => {
  const { data: customers } = useQuery({
    queryKey: ["customers"],
    queryFn: () =>
      CustomersService.readCustomers({ skip: 0, limit: 999 }),
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
  } = useForm<SaleCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      date_sale: "",
      amount: 0,
      description: "",
      customer_id: "",
      store_id: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: SaleCreate) =>
      SalesService.createSale({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Sale created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["sales"] })
    },
  })

  const onSubmit: SubmitHandler<SaleCreate> = (data) => {
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
          <ModalHeader>Add Sale</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.date_sale}>
              <FormLabel htmlFor="date_sale">Date Sale</FormLabel>
              <Input
                id="date_sale"
                type="date"
                placeholder="Select date sale"
                {...register("date_sale", {
                  required: "Date sale is required.",
                })}
              />
              {errors.date_sale && (
                <FormErrorMessage>{errors.date_sale.message}</FormErrorMessage>
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
            <FormControl isRequired isInvalid={!!errors.customer_id} mt={4}>
              <FormLabel htmlFor="customer_id">Customer</FormLabel>
              <Select
                id="customer_id"
                {...register("customer_id", {
                  required: "Customer of sale is required."
                })}
                placeholder="Select the customer">
                {customers?.data?.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name}
                  </option>
                ))}
              </Select>
              {errors.customer_id && (
                <FormErrorMessage>{errors.customer_id.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl isRequired isInvalid={!!errors.store_id} mt={4}>
              <FormLabel htmlFor="store_id">Store</FormLabel>
              <Select
                id="store_id"
                {...register("store_id", {
                  required: "Store of sale is required."
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

export default AddSale
