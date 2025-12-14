import React, { useState } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Badge,
  useToast,
  Card,
  CardBody,
  CardHeader,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Grid,
  GridItem,
  Divider,
  Spinner,
  Alert,
  AlertIcon,
  Progress,
} from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

import { OpenAPI } from '../../client/core/OpenAPI';

interface ExtractedInvoice {
  id: string;
  invoice_type: 'sales' | 'purchase';
  status: 'pending_review' | 'approved' | 'rejected' | 'converted';
  confidence_score: number;
  invoice_number?: string;
  invoice_date?: string;
  due_date?: string;
  vendor_name?: string;
  vendor_address?: string;
  vendor_vat_number?: string;
  customer_name?: string;
  customer_address?: string;
  customer_vat_number?: string;
  subtotal?: number;
  tax_amount?: number;
  total_amount?: number;
  currency: string;
  line_items: Array<{
    description?: string;
    quantity?: number;
    unit_price?: number;
    amount?: number;
    tax?: number;
  }>;
  date_created: string;
  document_upload?: {
    original_filename: string;
    file_size: number;
  };
}

const fetchExtractedInvoices = async (): Promise<ExtractedInvoice[]> => {
  const response = await fetch(`${OpenAPI.BASE}/api/v1/ai-invoices/`, {
    headers: {
      'Authorization': `Bearer ${OpenAPI.TOKEN}`,
    },
  });
  if (!response.ok) throw new Error('Failed to fetch invoices');
  return response.json();
};

const approveInvoice = async (id: string): Promise<ExtractedInvoice> => {
  const response = await fetch(`${OpenAPI.BASE}/api/v1/ai-invoices/${id}/approve`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OpenAPI.TOKEN}`,
    },
  });
  if (!response.ok) throw new Error('Failed to approve invoice');
  return response.json();
};

const rejectInvoice = async ({ id, reason }: { id: string; reason: string }): Promise<ExtractedInvoice> => {
  const response = await fetch(`${OpenAPI.BASE}/api/v1/ai-invoices/${id}/reject?rejection_reason=${encodeURIComponent(reason)}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OpenAPI.TOKEN}`,
    },
  });
  if (!response.ok) throw new Error('Failed to reject invoice');
  return response.json();
};

export const InvoiceReview: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedInvoice, setSelectedInvoice] = useState<ExtractedInvoice | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  const { data: invoices, isLoading, error } = useQuery({
    queryKey: ['extracted-invoices'],
    queryFn: fetchExtractedInvoices,
  });

  const approveMutation = useMutation({
    mutationFn: approveInvoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['extracted-invoices'] });
      queryClient.invalidateQueries({ queryKey: ['ai-invoices-stats'] });
      toast({
        title: t('aiInvoices.messages.approved'),
        status: 'success',
        duration: 3000,
      });
      onClose();
    },
    onError: (error: Error) => {
      toast({
        title: t('aiInvoices.messages.approveError'),
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectInvoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['extracted-invoices'] });
      queryClient.invalidateQueries({ queryKey: ['ai-invoices-stats'] });
      toast({
        title: t('aiInvoices.messages.rejected'),
        status: 'info',
        duration: 3000,
      });
      onClose();
      setRejectReason('');
    },
    onError: (error: Error) => {
      toast({
        title: t('aiInvoices.messages.rejectError'),
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  const handleViewDetails = (invoice: ExtractedInvoice) => {
    setSelectedInvoice(invoice);
    onOpen();
  };

  const handleApprove = () => {
    if (selectedInvoice) {
      approveMutation.mutate(selectedInvoice.id);
    }
  };

  const handleReject = () => {
    if (selectedInvoice && rejectReason.trim()) {
      rejectMutation.mutate({ id: selectedInvoice.id, reason: rejectReason });
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending_review: 'yellow',
      approved: 'green',
      rejected: 'red',
      converted: 'blue',
    };
    const labels: Record<string, string> = {
      pending_review: t('aiInvoices.statuses.pendingReview'),
      approved: t('aiInvoices.statuses.approved'),
      rejected: t('aiInvoices.statuses.rejected'),
      converted: t('aiInvoices.statuses.converted'),
    };
    return <Badge colorScheme={colors[status]}>{labels[status]}</Badge>;
  };

  const getConfidenceBadge = (score: number) => {
    const percentage = Math.round(score * 100);
    let color = 'red';
    if (percentage >= 80) color = 'green';
    else if (percentage >= 60) color = 'yellow';
    return (
      <HStack spacing={2}>
        <Progress value={percentage} size="sm" colorScheme={color} w="60px" borderRadius="full" />
        <Text fontSize="sm">{percentage}%</Text>
      </HStack>
    );
  };

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>{t('common.loading')}</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {t('aiInvoices.messages.loadError')}
      </Alert>
    );
  }

  const pendingInvoices = invoices?.filter(inv => inv.status === 'pending_review') || [];
  const processedInvoices = invoices?.filter(inv => inv.status !== 'pending_review') || [];

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Pending Review */}
        {pendingInvoices.length > 0 && (
          <Card>
            <CardHeader>
              <HStack justify="space-between">
                <Text fontWeight="bold" fontSize="lg">
                  {t('aiInvoices.pendingReview')} ({pendingInvoices.length})
                </Text>
              </HStack>
            </CardHeader>
            <CardBody pt={0}>
              <TableContainer>
                <Table size="sm">
                  <Thead>
                    <Tr>
                      <Th>{t('aiInvoices.fields.filename')}</Th>
                      <Th>{t('aiInvoices.fields.invoiceNumber')}</Th>
                      <Th>{t('aiInvoices.fields.vendor')}</Th>
                      <Th>{t('aiInvoices.fields.total')}</Th>
                      <Th>{t('aiInvoices.fields.confidence')}</Th>
                      <Th>{t('aiInvoices.fields.type')}</Th>
                      <Th>{t('common.actions')}</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {pendingInvoices.map((invoice) => (
                      <Tr key={invoice.id}>
                        <Td>{invoice.document_upload?.original_filename || '-'}</Td>
                        <Td>{invoice.invoice_number || '-'}</Td>
                        <Td>{invoice.vendor_name || '-'}</Td>
                        <Td>
                          {invoice.total_amount?.toFixed(2)} {invoice.currency}
                        </Td>
                        <Td>{getConfidenceBadge(invoice.confidence_score || 0)}</Td>
                        <Td>
                          <Badge colorScheme={invoice.invoice_type === 'purchase' ? 'purple' : 'teal'}>
                            {invoice.invoice_type === 'purchase' ? t('aiInvoices.types.purchase') : t('aiInvoices.types.sales')}
                          </Badge>
                        </Td>
                        <Td>
                          <Button size="sm" colorScheme="blue" onClick={() => handleViewDetails(invoice)}>
                            {t('aiInvoices.viewDetails')}
                          </Button>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </CardBody>
          </Card>
        )}

        {pendingInvoices.length === 0 && (
          <Alert status="info">
            <AlertIcon />
            {t('aiInvoices.messages.noPending')}
          </Alert>
        )}

        {/* Processed Invoices */}
        {processedInvoices.length > 0 && (
          <Card>
            <CardHeader>
              <Text fontWeight="bold" fontSize="lg">
                {t('aiInvoices.processedInvoices')} ({processedInvoices.length})
              </Text>
            </CardHeader>
            <CardBody pt={0}>
              <TableContainer>
                <Table size="sm">
                  <Thead>
                    <Tr>
                      <Th>{t('aiInvoices.fields.invoiceNumber')}</Th>
                      <Th>{t('aiInvoices.fields.vendor')}</Th>
                      <Th>{t('aiInvoices.fields.total')}</Th>
                      <Th>{t('fields.status')}</Th>
                      <Th>{t('fields.date')}</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {processedInvoices.map((invoice) => (
                      <Tr key={invoice.id} opacity={0.7}>
                        <Td>{invoice.invoice_number || '-'}</Td>
                        <Td>{invoice.vendor_name || '-'}</Td>
                        <Td>
                          {invoice.total_amount?.toFixed(2)} {invoice.currency}
                        </Td>
                        <Td>{getStatusBadge(invoice.status)}</Td>
                        <Td>{new Date(invoice.date_created).toLocaleDateString('bg-BG')}</Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </CardBody>
          </Card>
        )}
      </VStack>

      {/* Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {t('aiInvoices.invoiceDetails')}
            {selectedInvoice && getConfidenceBadge(selectedInvoice.confidence_score || 0)}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedInvoice && (
              <VStack spacing={4} align="stretch">
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.invoiceNumber')}</FormLabel>
                      <Input value={selectedInvoice.invoice_number || ''} isReadOnly />
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.invoiceDate')}</FormLabel>
                      <Input value={selectedInvoice.invoice_date || ''} isReadOnly />
                    </FormControl>
                  </GridItem>
                </Grid>

                <Divider />
                <Text fontWeight="bold">{t('aiInvoices.vendor')}</Text>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.name')}</FormLabel>
                      <Input value={selectedInvoice.vendor_name || ''} isReadOnly />
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.vatNumber')}</FormLabel>
                      <Input value={selectedInvoice.vendor_vat_number || ''} isReadOnly />
                    </FormControl>
                  </GridItem>
                  <GridItem colSpan={2}>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.address')}</FormLabel>
                      <Input value={selectedInvoice.vendor_address || ''} isReadOnly />
                    </FormControl>
                  </GridItem>
                </Grid>

                <Divider />
                <Text fontWeight="bold">{t('aiInvoices.amounts')}</Text>
                <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.subtotal')}</FormLabel>
                      <Input value={`${selectedInvoice.subtotal?.toFixed(2) || '0.00'} ${selectedInvoice.currency}`} isReadOnly />
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.vat')}</FormLabel>
                      <Input value={`${selectedInvoice.tax_amount?.toFixed(2) || '0.00'} ${selectedInvoice.currency}`} isReadOnly />
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel fontSize="sm" color="gray.500">{t('aiInvoices.fields.total')}</FormLabel>
                      <Input value={`${selectedInvoice.total_amount?.toFixed(2) || '0.00'} ${selectedInvoice.currency}`} isReadOnly fontWeight="bold" />
                    </FormControl>
                  </GridItem>
                </Grid>

                {selectedInvoice.line_items && selectedInvoice.line_items.length > 0 && (
                  <>
                    <Divider />
                    <Text fontWeight="bold">{t('aiInvoices.lineItems')}</Text>
                    <TableContainer>
                      <Table size="sm">
                        <Thead>
                          <Tr>
                            <Th>{t('aiInvoices.fields.description')}</Th>
                            <Th isNumeric>{t('aiInvoices.fields.quantity')}</Th>
                            <Th isNumeric>{t('aiInvoices.fields.unitPrice')}</Th>
                            <Th isNumeric>{t('aiInvoices.fields.amount')}</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {selectedInvoice.line_items.map((item, index) => (
                            <Tr key={index}>
                              <Td>{item.description || '-'}</Td>
                              <Td isNumeric>{item.quantity || '-'}</Td>
                              <Td isNumeric>{item.unit_price?.toFixed(2) || '-'}</Td>
                              <Td isNumeric>{item.amount?.toFixed(2) || '-'}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </>
                )}

                {selectedInvoice.status === 'pending_review' && (
                  <>
                    <Divider />
                    <FormControl>
                      <FormLabel>{t('aiInvoices.rejectReason')}</FormLabel>
                      <Textarea
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                        placeholder={t('aiInvoices.rejectReasonPlaceholder')}
                      />
                    </FormControl>
                  </>
                )}
              </VStack>
            )}
          </ModalBody>

          <ModalFooter>
            {selectedInvoice?.status === 'pending_review' && (
              <HStack spacing={3}>
                <Button
                  colorScheme="red"
                  variant="outline"
                  onClick={handleReject}
                  isLoading={rejectMutation.isPending}
                  isDisabled={!rejectReason.trim()}
                >
                  {t('aiInvoices.reject')}
                </Button>
                <Button
                  colorScheme="green"
                  onClick={handleApprove}
                  isLoading={approveMutation.isPending}
                >
                  {t('aiInvoices.approve')}
                </Button>
              </HStack>
            )}
            <Button ml={3} onClick={onClose}>
              {t('common.close')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default InvoiceReview;
