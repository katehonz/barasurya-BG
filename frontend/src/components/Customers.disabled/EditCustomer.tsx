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
  type CustomerPublic,
  type CustomerUpdate,
  CustomersService,
  CustomerTypesService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"
import { useEffect } from "react"

interface EditCustomerProps {
  customer: CustomerPublic
  isOpen: boolean
  onClose: () => void
}

const EditCustomer = ({ customer, isOpen, onClose }: EditCustomerProps) => {
  const { data: customer_types } = useQuery({
    queryKey: ["customer_types"],
    queryFn: () =>
      CustomerTypesService.readCustomerTypes({ skip: 0, limit: 999 }),
  })

  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<CustomerUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: customer,
  })

  useEffect(() => {
    if (isOpen) {
      reset(customer)
    }
  }, [customer, isOpen, reset])

  const mutation = useMutation({
    mutationFn: (data: CustomerUpdate) =>
      CustomersService.updateCustomer({ id: customer.id, requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Customer updated successfully.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] })
    },
  })

  const onSubmit: SubmitHandler<CustomerUpdate> = async (data) => {
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
          <ModalHeader>Edit Customer</ModalHeader>
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
            <FormControl isRequired isInvalid={!!errors.customer_type_id} mt={4}>
              <FormLabel htmlFor="customer_type_id">Category</FormLabel>
              <Select
                id="customer_type_id"
                {...register("customer_type_id", {
                  required: "Category of customer is required."
                })}
                placeholder="Select the type of customer">
                {customer_types?.data?.map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name}
                  </option>
                ))}
              </Select>
              {errors.customer_type_id && (
                <FormErrorMessage>{errors.customer_type_id.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="phone">Phone</FormLabel>
              <Input
                id="phone"
                {...register("phone")}
                placeholder="081234567890"
                type="text"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="address">Address</FormLabel>
              <Input
                id="address"
                {...register("address")}
                placeholder="Jl. Sultan Agung No. 1"
                type="text"
              />
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

export default EditCustomer
