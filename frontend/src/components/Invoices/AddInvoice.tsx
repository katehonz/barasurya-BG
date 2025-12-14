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
  VStack,
  Grid,
  GridItem,
  Heading,
  Textarea,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Text,
  Checkbox,
  InputGroup,
} from "@chakra-ui/react"
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query"
import { type SubmitHandler, useForm, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useState, useEffect, useMemo } from "react"
import { useTranslation } from "react-i18next"

import { InvoicesService, type InvoiceCreate, ContraagentsService, type ContraagentPublic, OrganizationsService } from "../../client"

// Define VatDocumentType locally since it's not exported from client
enum VatDocumentType {
  INVOICE = "01",
  DEBIT_NOTE = "02",
  CREDIT_NOTE = "03",
  PROFORMA_INVOICE = "04",
}

// Temporary product type for search
interface ProductPublic {
  id: string
  name: string
  description?: string
  sku?: string
  price: number
  tax_rate: number
}
import useCustomToast from "../../hooks/useCustomToast"
import SearchModal from "../Common/SearchModal"


const AddInvoiceSchema = z.object({
  invoice_no: z.string().min(1, "Invoice number is required."),
  contact_id: z.string().uuid("Contact is required."),
  issue_date: z.string().min(1, "Issue date is required."),
  due_date: z.string().optional(),
  tax_event_date: z.string().optional(),
  billing_name: z.string().min(1, "Billing name is required."),
  billing_address: z.string().optional(),
  billing_vat_number: z.string().optional(),
  billing_company_id: z.string().optional(),
  payment_method: z.string().optional(),
  notes: z.string().optional(),
  vat_document_type: z.nativeEnum(VatDocumentType),
  oss_enabled: z.boolean().optional(),
  oss_country: z.string().optional(),
  vat_reason: z.string().optional(),
  invoice_lines: z.array(z.object({
    description: z.string().min(1, "Description is required."),
    quantity: z.number().min(0),
    unit_price: z.number().min(0),
    tax_rate: z.number().min(0),
    discount_percent: z.number().min(0).max(100),
    product_id: z.string().uuid().optional(),
  })).min(1, "At least one invoice line is required."),
})

interface AddInvoiceProps {
  isOpen: boolean
  onClose: () => void
}

const euCountries = [
  { code: "AT", name: "Austria" },
  { code: "BE", name: "Belgium" },
  { code: "BG", name: "Bulgaria" },
  { code: "HR", name: "Croatia" },
  { code: "CY", name: "Cyprus" },
  { code: "CZ", name: "Czech Republic" },
  { code: "DK", name: "Denmark" },
  { code: "EE", name: "Estonia" },
  { code: "FI", name: "Finland" },
  { code: "FR", name: "France" },
  { code: "DE", name: "Germany" },
  { code: "GR", name: "Greece" },
  { code: "HU", name: "Hungary" },
  { code: "IE", name: "Ireland" },
  { code: "IT", name: "Italy" },
  { code: "LV", name: "Latvia" },
  { code: "LT", name: "Lithuania" },
  { code: "LU", name: "Luxembourg" },
  { code: "MT", name: "Malta" },
  { code: "NL", name: "Netherlands" },
  { code: "PL", name: "Poland" },
  { code: "PT", name: "Portugal" },
  { code: "RO", name: "Romania" },
  { code: "SK", name: "Slovakia" },
  { code: "SI", name: "Slovenia" },
  { code: "ES", name: "Spain" },
  { code: "SE", name: "Sweden" },
]

// Mock VAT zero reasons for demonstration. In a real app, this would come from an API.
const vatZeroReasons = [
  { code: "01", description: "Intra-community supply" },
  { code: "02", description: "Export" },
  { code: "03", description: "Services abroad" },
  { code: "99", description: "Other reason" },
]


export default function AddInvoice({ isOpen, onClose }: AddInvoiceProps) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const { data: currentOrganization } = useQuery({
    queryKey: ["currentOrganization"],
    queryFn: OrganizationsService.readCurrentOrganization,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
    setValue,
    watch,
  } = useForm<InvoiceCreate>({
    resolver: zodResolver(AddInvoiceSchema),
    defaultValues: {
      issue_date: new Date().toISOString().split("T")[0],
      vat_document_type: VatDocumentType.INVOICE,
      oss_enabled: false,
      invoice_lines: [{ description: "", quantity: 1, unit_price: 0, tax_rate: 20, discount_percent: 0 }],
    }
  })

  const { fields, append, remove, update } = useFieldArray({
    control,
    name: "invoice_lines",
  })

  const [isContactSearchModalOpen, setIsContactSearchModalOpen] = useState(false)
  const [selectedContactName, setSelectedContactName] = useState<string | undefined>(undefined)
  const [isProductSearchModalOpen, setIsProductSearchModalOpen] = useState(false)
  const [currentLineIndex, setCurrentLineIndex] = useState<number | null>(null)

  // State for calculated totals
  const [invoiceSubtotal, setInvoiceSubtotal] = useState(0)
  const [invoiceTax, setInvoiceTax] = useState(0)
  const [invoiceTotal, setInvoiceTotal] = useState(0)

  // Watch for changes in invoice_lines
  const watchedInvoiceLines = watch("invoice_lines")
  const watchedOssEnabled = watch("oss_enabled")

  // Use the actual VAT registered status from the organization settings
  const isCompanyVatRegistered = currentOrganization?.is_vat_registered || false; 

  // Determine if VAT reason field should be shown
  const showVatReason = useMemo(() => {
    return isCompanyVatRegistered && watchedInvoiceLines.some(line => (line.tax_rate || 0) === 0);
  }, [isCompanyVatRegistered, watchedInvoiceLines])

  useEffect(() => {
    let subtotal = 0
    let tax = 0

    watchedInvoiceLines.forEach((line) => {
      const quantity = line.quantity || 0
      const unitPrice = line.unit_price || 0
      const discountPercent = line.discount_percent || 0
      const taxRate = line.tax_rate || 0

      const lineGross = quantity * unitPrice
      const lineDiscountAmount = lineGross * (discountPercent / 100)
      const lineSubtotal = lineGross - lineDiscountAmount
      const lineTax = lineSubtotal * (taxRate / 100)

      subtotal += lineSubtotal
      tax += lineTax
    })

    setInvoiceSubtotal(subtotal)
    setInvoiceTax(tax)
    setInvoiceTotal(subtotal + tax)
  }, [watchedInvoiceLines])

  const handleContactSelect = (contact: ContraagentPublic) => {
    setValue("contact_id", contact.id)
    setValue("billing_name", contact.name)
    setValue("billing_address", contact.street_name || "")
    setValue("billing_vat_number", contact.vat_number || "")
    setValue("billing_company_id", contact.registration_number || "")
    setSelectedContactName(contact.name)
    setIsContactSearchModalOpen(false)
  }

  const handleProductSelect = (product: ProductPublic) => {
    if (currentLineIndex !== null) {
      update(currentLineIndex, {
        ...fields[currentLineIndex],
        product_id: product.id,
        description: product.description || product.name,
        unit_price: product.price,
        tax_rate: product.tax_rate,
      })
    }
    setIsProductSearchModalOpen(false)
    setCurrentLineIndex(null)
  }

  const searchContacts = async (query: string) => {
    const response = await ContraagentsService.readContraagents({ search: query, isCustomer: true })
    return response.data
  }

  const searchProducts = async (_query: string): Promise<ProductPublic[]> => {
    // TODO: Implement product search when Products API is available
    return []
  }

  const mutation = useMutation({
    mutationFn: (data: InvoiceCreate) =>
      InvoicesService.createInvoice({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Invoice created successfully.", "success")
      queryClient.invalidateQueries({ queryKey: ["invoices"] })
      onClose()
    },
    onError: (err) => {
      const errDetail = (err as any).body?.detail
      showToast("Error", `Something went wrong: ${errDetail}`, "error")
    },
  })

  const onSubmit: SubmitHandler<InvoiceCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="4xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Invoice</ModalHeader>
        <ModalCloseButton />
        <form onSubmit={handleSubmit(onSubmit)}>
          <ModalBody>
            <VStack spacing={4} as="fieldset">
              <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full">
                <GridItem>
                  <FormControl isInvalid={!!errors.invoice_no}>
                    <FormLabel htmlFor="invoice_no">Invoice Number</FormLabel>
                    <Input
                      id="invoice_no"
                      {...register("invoice_no")}
                      type="text"
                    />
                    <FormErrorMessage>{errors.invoice_no?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                   <FormControl isInvalid={!!errors.contact_id}>
                    <FormLabel htmlFor="contact_id">Contact</FormLabel>
                    <InputGroup>
                      <Input
                        id="contact_name"
                        value={selectedContactName || ""}
                        readOnly
                        placeholder="Select a contact"
                        onClick={() => setIsContactSearchModalOpen(true)}
                      />
                      <Button onClick={() => setIsContactSearchModalOpen(true)} ml={1}>Search</Button>
                    </InputGroup>
                    <Input type="hidden" {...register("contact_id")} />
                    <FormErrorMessage>{errors.contact_id?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
              </Grid>
              
              <Heading size="md" alignSelf="flex-start" mt={6}>Dates</Heading>
              <Grid templateColumns="repeat(3, 1fr)" gap={4} w="full">
                <GridItem>
                  <FormControl isInvalid={!!errors.issue_date}>
                    <FormLabel htmlFor="issue_date">Issue Date</FormLabel>
                    <Input
                      id="issue_date"
                      {...register("issue_date")}
                      type="date"
                    />
                    <FormErrorMessage>{errors.issue_date?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                  <FormControl isInvalid={!!errors.due_date}>
                    <FormLabel htmlFor="due_date">Due Date</FormLabel>
                    <Input
                      id="due_date"
                      {...register("due_date")}
                      type="date"
                    />
                    <FormErrorMessage>{errors.due_date?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                  <FormControl isInvalid={!!errors.tax_event_date}>
                    <FormLabel htmlFor="tax_event_date">Tax Event Date</FormLabel>
                    <Input
                      id="tax_event_date"
                      {...register("tax_event_date")}
                      type="date"
                    />
                    <FormErrorMessage>{errors.tax_event_date?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
              </Grid>

              <Heading size="md" alignSelf="flex-start" mt={6}>Billing Information</Heading>
              <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full">
                <GridItem colSpan={2}>
                  <FormControl isInvalid={!!errors.billing_name}>
                    <FormLabel htmlFor="billing_name">Billing Name</FormLabel>
                    <Input
                      id="billing_name"
                      {...register("billing_name")}
                      type="text"
                    />
                    <FormErrorMessage>{errors.billing_name?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem colSpan={2}>
                  <FormControl isInvalid={!!errors.billing_address}>
                    <FormLabel htmlFor="billing_address">Billing Address</FormLabel>
                    <Input
                      id="billing_address"
                      {...register("billing_address")}
                      type="text"
                    />
                    <FormErrorMessage>{errors.billing_address?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                  <FormControl isInvalid={!!errors.billing_vat_number}>
                    <FormLabel htmlFor="billing_vat_number">VAT Number</FormLabel>
                    <Input
                      id="billing_vat_number"
                      {...register("billing_vat_number")}
                      type="text"
                    />
                    <FormErrorMessage>{errors.billing_vat_number?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                  <FormControl isInvalid={!!errors.billing_company_id}>
                    <FormLabel htmlFor="billing_company_id">Company ID</FormLabel>
                    <Input
                      id="billing_company_id"
                      {...register("billing_company_id")}
                      type="text"
                    />
                    <FormErrorMessage>{errors.billing_company_id?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
              </Grid>
              
              <Heading size="md" alignSelf="flex-start" mt={6}>Payment Information</Heading>
              <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full">
                <GridItem>
                   <FormControl isInvalid={!!errors.payment_method}>
                    <FormLabel htmlFor="payment_method">Payment Method</FormLabel>
                    <Select id="payment_method" {...register("payment_method")}>
                      <option value="cash">Cash</option>
                      <option value="bank">Bank Transfer</option>
                      <option value="card">Card</option>
                    </Select>
                    <FormErrorMessage>{errors.payment_method?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
                <GridItem>
                  <FormControl isInvalid={!!errors.vat_document_type}>
                    <FormLabel htmlFor="vat_document_type">VAT Document Type</FormLabel>
                    <Select id="vat_document_type" {...register("vat_document_type")}>
                      {Object.values(VatDocumentType).map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </Select>
                    <FormErrorMessage>{errors.vat_document_type?.message}</FormErrorMessage>
                  </FormControl>
                </GridItem>
              </Grid>
              
              <FormControl isInvalid={!!errors.notes} mt={4}>
                <FormLabel htmlFor="notes">Notes</FormLabel>
                <Textarea
                  id="notes"
                  {...register("notes")}
                />
                <FormErrorMessage>{errors.notes?.message}</FormErrorMessage>
              </FormControl>

              {/* VAT and OSS Logic */}
              <Heading size="md" alignSelf="flex-start" mt={6}>VAT and OSS Details</Heading>
              <VStack spacing={4} align="stretch" w="full">
                <FormControl>
                  <Checkbox 
                    {...register("oss_enabled")} 
                    onChange={(e) => {
                      if (!e.target.checked) {
                        setValue("oss_country", undefined);
                      }
                    }}
                  >
                    Enable OSS (One-Stop Shop) regime
                  </Checkbox>
                </FormControl>
                {watchedOssEnabled && (
                  <FormControl isInvalid={!!errors.oss_country}>
                    <FormLabel htmlFor="oss_country">OSS Country</FormLabel>
                    <Select id="oss_country" {...register("oss_country")}>
                      <option value="">Select country...</option>
                      {euCountries.map((country) => (
                        <option key={country.code} value={country.code}>
                          {country.name} ({country.code})
                        </option>
                      ))}
                    </Select>
                    <FormErrorMessage>{errors.oss_country?.message}</FormErrorMessage>
                  </FormControl>
                )}

                {showVatReason && (
                  <FormControl isInvalid={!!errors.vat_reason}>
                    <FormLabel htmlFor="vat_reason">VAT Zero Reason</FormLabel>
                    <Select id="vat_reason" {...register("vat_reason")}>
                      <option value="">Select reason...</option>
                      {vatZeroReasons.map((reason) => (
                        <option key={reason.code} value={reason.code}>
                          {reason.description}
                        </option>
                      ))}
                    </Select>
                    <FormErrorMessage>{errors.vat_reason?.message}</FormErrorMessage>
                  </FormControl>
                )}
              </VStack>


              <Heading size="md" alignSelf="flex-start" mt={6}>Invoice Lines</Heading>
              <TableContainer w="full">
                <Table>
                  <Thead>
                    <Tr>
                      <Th>Description</Th>
                      <Th isNumeric>Quantity</Th>
                      <Th isNumeric>Unit Price</Th>
                      <Th isNumeric>Tax Rate</Th>
                      <Th></Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {fields.map((field, index) => (
                      <Tr key={field.id}>
                        <Td>
                          <FormControl isInvalid={!!errors.invoice_lines?.[index]?.description}>
                            <InputGroup>
                              <Input
                                {...register(`invoice_lines.${index}.description` as const)}
                                placeholder="Item description"
                                onClick={() => {
                                  setCurrentLineIndex(index)
                                  setIsProductSearchModalOpen(true)
                                }}
                              />
                              <Button
                                ml={1}
                                onClick={() => {
                                  setCurrentLineIndex(index)
                                  setIsProductSearchModalOpen(true)
                                }}
                              >
                                Search Product
                              </Button>
                            </InputGroup>
                            <Input type="hidden" {...register(`invoice_lines.${index}.product_id`)} />
                            <FormErrorMessage>
                              {errors.invoice_lines?.[index]?.description?.message}
                            </FormErrorMessage>
                          </FormControl>
                        </Td>
                        <Td>
                          <FormControl isInvalid={!!errors.invoice_lines?.[index]?.quantity}>
                            <Input
                              {...register(`invoice_lines.${index}.quantity` as const, { valueAsNumber: true })}
                              type="number"
                              step="0.01"
                            />
                             <FormErrorMessage>
                              {errors.invoice_lines?.[index]?.quantity?.message}
                            </FormErrorMessage>
                          </FormControl>
                        </Td>
                        <Td>
                           <FormControl isInvalid={!!errors.invoice_lines?.[index]?.unit_price}>
                            <Input
                              {...register(`invoice_lines.${index}.unit_price` as const, { valueAsNumber: true })}
                              type="number"
                              step="0.01"
                            />
                             <FormErrorMessage>
                              {errors.invoice_lines?.[index]?.unit_price?.message}
                            </FormErrorMessage>
                          </FormControl>
                        </Td>
                        <Td>
                          <FormControl isInvalid={!!errors.invoice_lines?.[index]?.tax_rate}>
                            <Input
                              {...register(`invoice_lines.${index}.tax_rate` as const, { valueAsNumber: true })}
                              type="number"
                              step="0.01"
                            />
                            <FormErrorMessage>
                              {errors.invoice_lines?.[index]?.tax_rate?.message}
                            </FormErrorMessage>
                          </FormControl>
                        </Td>
                        <Td>
                          <Button colorScheme="red" size="sm" onClick={() => remove(index)}>
                            Remove
                          </Button>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
              <Button
                onClick={() => append({ description: "", quantity: 1, unit_price: 0, tax_rate: 20, discount_percent: 0 })}
                alignSelf="flex-start"
              >
                Add Line
              </Button>

              {/* Totals Summary */}
              <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full" mt={4}>
                <GridItem colSpan={1} /> {/* Empty column for alignment */}
                <GridItem colSpan={1}>
                  <Text textAlign="right" fontWeight="bold">Subtotal: {invoiceSubtotal.toFixed(2)}</Text>
                  <Text textAlign="right" fontWeight="bold">Tax: {invoiceTax.toFixed(2)}</Text>
                  <Text textAlign="right" fontWeight="extrabold" fontSize="xl">Total: {invoiceTotal.toFixed(2)}</Text>
                </GridItem>
              </Grid>

            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              mr={3}
              type="submit"
              isLoading={isSubmitting}
            >
              Save
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
      <SearchModal<ContraagentPublic>
        isOpen={isContactSearchModalOpen}
        onClose={() => setIsContactSearchModalOpen(false)}
        title="Search Contact"
        searchFun={searchContacts}
        onSelect={handleContactSelect}
        displayFields={[
          { key: "name", label: "Name" },
          { key: "vat_number", label: "VAT No.", format: (value) => value || "N/A" },
          { key: "eik", label: "EIK", format: (value) => value || "N/A" },
        ]}
      />
      <SearchModal<ProductPublic>
        isOpen={isProductSearchModalOpen}
        onClose={() => setIsProductSearchModalOpen(false)}
        title="Search Product"
        searchFun={searchProducts}
        onSelect={handleProductSelect}
        displayFields={[
          { key: "name", label: "Name" },
          { key: "sku", label: "SKU", format: (value) => value || "N/A" },
          { key: "price", label: "Price", format: (value) => value?.toString() || "N/A" },
        ]}
      />
    </Modal>
  )
}
