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
  Switch,
  Textarea,
  HStack,
  VStack,
  Divider,
  Text,
  Alert,
  AlertIcon,
  useDisclosure,
  Collapse,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm, Controller } from "react-hook-form"
import { useState } from "react"

import { type ApiError, type ContraagentCreate, ContraagentsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddContraagentProps {
  isOpen: boolean
  onClose: () => void
}

interface ContraagentFormData extends ContraagentCreate {
  validateVat?: boolean
}

const AddContraagent = ({ isOpen, onClose }: AddContraagentProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const [vatValidation, setVatValidation] = useState<any>(null)
  const [isVatValidating, setIsVatValidating] = useState(false)
  const { isOpen: isAdvancedOpen, onToggle: onAdvancedToggle } = useDisclosure()

  const {
    register,
    control,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<ContraagentFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      website: "",
      fax: "",
      is_company: true,
      is_customer: false,
      is_supplier: false,
      is_active: true,
      registration_number: "",
      vat_number: "",
      street_name: "",
      building_number: "",
      building: "",
      postal_code: "",
      city: "",
      region: "",
      country: "BG",
      additional_address_detail: "",
      contact_person_title: "",
      contact_person_first_name: "",
      contact_person_last_name: "",
      tax_type: "",
      tax_authority: "",
      self_billing_indicator: false,
      related_party: false,
      iban_number: "",
      bank_account_number: "",
      bank_sort_code: "",
      opening_debit_balance: 0,
      opening_credit_balance: 0,
      name_latin: "",
      name_cyrillic: "",
      notes: "",
      validateVat: true,
    },
  })

  const watchedVatNumber = watch("vat_number")

  // VAT validation mutation
  const vatValidationMutation = useMutation({
    mutationFn: (vatNumber: string) =>
      fetch(`/api/v1/contraagents/validate-vat?vat_number=${encodeURIComponent(vatNumber)}`)
        .then(res => res.json()),
    onSuccess: (data) => {
      setVatValidation(data)
      setIsVatValidating(false)
      
      if (data.valid) {
        showToast("VAT Valid", "VAT number is valid", "success")
        // Auto-fill fields if available
        if (data.company_name && !watch("name")) {
          setValue("name", data.company_name)
        }
        if (data.eik && !watch("registration_number")) {
          setValue("registration_number", data.eik)
        }
      } else {
        showToast("VAT Invalid", data.error || "VAT number validation failed", "error")
      }
    },
    onError: () => {
      setIsVatValidating(false)
      showToast("Error", "Failed to validate VAT number", "error")
    },
  })

  const validateVatNumber = () => {
    const vatNumber = watchedVatNumber
    if (!vatNumber) return
    
    setIsVatValidating(true)
    vatValidationMutation.mutate(vatNumber)
  }

  const mutation = useMutation({
    mutationFn: (data: ContraagentFormData) => {
      const { validateVat, ...requestBody } = data
      return ContraagentsService.createContraagent({
        requestBody: requestBody as ContraagentCreate,
        validateVat: validateVat ?? true
      })
    },
    onSuccess: () => {
      showToast("Success!", "Contraagent created successfully.", "success")
      reset()
      setVatValidation(null)
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["contraagents"] })
    },
  })

  const onSubmit: SubmitHandler<ContraagentFormData> = (data) => {
    // Ensure at least customer or supplier is selected
    if (!data.is_customer && !data.is_supplier) {
      showToast("Error", "Please select at least Customer or Supplier", "error")
      return
    }
    
    mutation.mutate(data)
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "2xl", lg: "4xl" }}
        isCentered
        scrollBehavior="inside"
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Add Contraagent</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4} align="stretch">
              {/* Basic Information */}
              <FormControl isRequired isInvalid={!!errors.name}>
                <FormLabel htmlFor="name">Name</FormLabel>
                <Input
                  id="name"
                  {...register("name", {
                    required: "Name is required.",
                  })}
                  placeholder="Company or Person Name"
                  type="text"
                />
                {errors.name && (
                  <FormErrorMessage>{errors.name.message}</FormErrorMessage>
                )}
              </FormControl>

              <HStack spacing={4}>
                <FormControl isInvalid={!!errors.email}>
                  <FormLabel htmlFor="email">Email</FormLabel>
                  <Input
                    id="email"
                    {...register("email")}
                    placeholder="email@example.com"
                    type="email"
                  />
                  {errors.email && (
                    <FormErrorMessage>{errors.email.message}</FormErrorMessage>
                  )}
                </FormControl>

                <FormControl isInvalid={!!errors.phone}>
                  <FormLabel htmlFor="phone">Phone</FormLabel>
                  <Input
                    id="phone"
                    {...register("phone")}
                    placeholder="+359 888 123 456"
                    type="tel"
                  />
                  {errors.phone && (
                    <FormErrorMessage>{errors.phone.message}</FormErrorMessage>
                  )}
                </FormControl>
              </HStack>

              {/* Classification */}
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>Is Company</FormLabel>
                  <Controller
                    name="is_company"
                    control={control}
                    render={({ field: { value, onChange, ...rest } }) => (
                      <Switch {...rest} isChecked={value} onChange={onChange} />
                    )}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Is Customer</FormLabel>
                  <Controller
                    name="is_customer"
                    control={control}
                    render={({ field: { value, onChange, ...rest } }) => (
                      <Switch {...rest} isChecked={value} onChange={onChange} />
                    )}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Is Supplier</FormLabel>
                  <Controller
                    name="is_supplier"
                    control={control}
                    render={({ field: { value, onChange, ...rest } }) => (
                      <Switch {...rest} isChecked={value} onChange={onChange} />
                    )}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Is Active</FormLabel>
                  <Controller
                    name="is_active"
                    control={control}
                    render={({ field: { value, onChange, ...rest } }) => (
                      <Switch {...rest} isChecked={value} onChange={onChange} />
                    )}
                  />
                </FormControl>
              </HStack>

              {/* Registration Numbers */}
              <HStack spacing={4}>
                <FormControl isInvalid={!!errors.registration_number}>
                  <FormLabel htmlFor="registration_number">Registration Number (ЕИК/БУЛСТАТ)</FormLabel>
                  <Input
                    id="registration_number"
                    {...register("registration_number")}
                    placeholder="123456789"
                    type="text"
                  />
                  {errors.registration_number && (
                    <FormErrorMessage>{errors.registration_number.message}</FormErrorMessage>
                  )}
                </FormControl>

                <FormControl isInvalid={!!errors.vat_number}>
                  <FormLabel htmlFor="vat_number">VAT Number</FormLabel>
                  <HStack>
                    <Input
                      id="vat_number"
                      {...register("vat_number")}
                      placeholder="BG123456789"
                      type="text"
                      flex={1}
                    />
                    <Button
                      size="sm"
                      onClick={validateVatNumber}
                      isLoading={isVatValidating}
                      isDisabled={!watchedVatNumber}
                    >
                      Validate
                    </Button>
                  </HStack>
                  {errors.vat_number && (
                    <FormErrorMessage>{errors.vat_number.message}</FormErrorMessage>
                  )}
                </FormControl>
              </HStack>

              {/* VAT Validation Result */}
              {vatValidation && (
                <Alert status={vatValidation.valid ? "success" : "warning"}>
                  <AlertIcon />
                  <Text>
                    {vatValidation.valid 
                      ? `Valid VAT: ${vatValidation.company_name || 'Company'} (${vatValidation.country_code})`
                      : vatValidation.error
                    }
                  </Text>
                </Alert>
              )}

              {/* VAT Validation Toggle */}
              <FormControl>
                <Controller
                  name="validateVat"
                  control={control}
                  render={({ field: { value, onChange, ...rest } }) => (
                    <Switch {...rest} isChecked={value} onChange={onChange}>
                      Validate VAT number on save
                    </Switch>
                  )}
                />
              </FormControl>

              <Divider />

              {/* Advanced Fields Toggle */}
              <Button
                variant="outline"
                onClick={onAdvancedToggle}
                alignSelf="flex-start"
              >
                {isAdvancedOpen ? "Hide" : "Show"} Advanced Fields
              </Button>

              <Collapse in={isAdvancedOpen} animateOpacity>
                <VStack spacing={4} align="stretch">
                  {/* Address Information */}
                  <Text fontWeight="bold">Address Information</Text>
                  
                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.street_name}>
                      <FormLabel htmlFor="street_name">Street Name</FormLabel>
                      <Input
                        id="street_name"
                        {...register("street_name")}
                        placeholder="Vitosha Blvd."
                        type="text"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.building_number}>
                      <FormLabel htmlFor="building_number">Building Number</FormLabel>
                      <Input
                        id="building_number"
                        {...register("building_number")}
                        placeholder="1"
                        type="text"
                      />
                    </FormControl>
                  </HStack>

                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.city}>
                      <FormLabel htmlFor="city">City</FormLabel>
                      <Input
                        id="city"
                        {...register("city")}
                        placeholder="Sofia"
                        type="text"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.postal_code}>
                      <FormLabel htmlFor="postal_code">Postal Code</FormLabel>
                      <Input
                        id="postal_code"
                        {...register("postal_code")}
                        placeholder="1000"
                        type="text"
                      />
                    </FormControl>
                  </HStack>

                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.region}>
                      <FormLabel htmlFor="region">Region</FormLabel>
                      <Input
                        id="region"
                        {...register("region")}
                        placeholder="Sofia-grad"
                        type="text"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.country}>
                      <FormLabel htmlFor="country">Country</FormLabel>
                      <Input
                        id="country"
                        {...register("country")}
                        placeholder="BG"
                        type="text"
                      />
                    </FormControl>
                  </HStack>

                  {/* Contact Person */}
                  <Text fontWeight="bold">Contact Person</Text>
                  
                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.contact_person_first_name}>
                      <FormLabel htmlFor="contact_person_first_name">First Name</FormLabel>
                      <Input
                        id="contact_person_first_name"
                        {...register("contact_person_first_name")}
                        placeholder="John"
                        type="text"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.contact_person_last_name}>
                      <FormLabel htmlFor="contact_person_last_name">Last Name</FormLabel>
                      <Input
                        id="contact_person_last_name"
                        {...register("contact_person_last_name")}
                        placeholder="Doe"
                        type="text"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.contact_person_title}>
                      <FormLabel htmlFor="contact_person_title">Title</FormLabel>
                      <Input
                        id="contact_person_title"
                        {...register("contact_person_title")}
                        placeholder="Mr."
                        type="text"
                      />
                    </FormControl>
                  </HStack>

                  {/* Bank Information */}
                  <Text fontWeight="bold">Bank Information</Text>
                  
                  <FormControl isInvalid={!!errors.iban_number}>
                    <FormLabel htmlFor="iban_number">IBAN</FormLabel>
                    <Input
                      id="iban_number"
                      {...register("iban_number")}
                      placeholder="BG80 BNBG 9661 1020 3456 78"
                      type="text"
                    />
                  </FormControl>

                  {/* Opening Balances */}
                  <Text fontWeight="bold">Opening Balances</Text>
                  
                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.opening_debit_balance}>
                      <FormLabel htmlFor="opening_debit_balance">Debit Balance</FormLabel>
                      <Input
                        id="opening_debit_balance"
                        {...register("opening_debit_balance", { valueAsNumber: true })}
                        placeholder="0.00"
                        type="number"
                        step="0.01"
                      />
                    </FormControl>

                    <FormControl isInvalid={!!errors.opening_credit_balance}>
                      <FormLabel htmlFor="opening_credit_balance">Credit Balance</FormLabel>
                      <Input
                        id="opening_credit_balance"
                        {...register("opening_credit_balance", { valueAsNumber: true })}
                        placeholder="0.00"
                        type="number"
                        step="0.01"
                      />
                    </FormControl>
                  </HStack>

                  {/* Notes */}
                  <FormControl isInvalid={!!errors.notes}>
                    <FormLabel htmlFor="notes">Notes</FormLabel>
                    <Textarea
                      id="notes"
                      {...register("notes")}
                      placeholder="Additional notes..."
                      rows={3}
                    />
                  </FormControl>
                </VStack>
              </Collapse>
            </VStack>
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

export default AddContraagent