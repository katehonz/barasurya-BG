import React, { useCallback, useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress,
  useToast,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Select,
  Icon,
} from '@chakra-ui/react';
import { FiUpload, FiFile, FiAlertCircle } from 'react-icons/fi';
import { useDropzone } from 'react-dropzone';
import { useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

import { OpenAPI } from '../../client/core/OpenAPI';

interface ProcessingStats {
  total: number;
  pending_review: number;
  approved: number;
  rejected: number;
}

export const InvoiceUpload: React.FC = () => {
  const { t } = useTranslation();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingFiles, setProcessingFiles] = useState<string[]>([]);
  const [invoiceType, setInvoiceType] = useState<'sales' | 'purchase'>('purchase');
  const [stats, setStats] = useState<ProcessingStats | null>(null);

  const toast = useToast();
  const queryClient = useQueryClient();

  // Fetch stats on mount
  React.useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${OpenAPI.BASE}/api/v1/ai-invoices/stats/summary`, {
          headers: {
            'Authorization': `Bearer ${OpenAPI.TOKEN}`,
          },
        });
        if (response.ok) {
          setStats(await response.json());
        }
      } catch (e) {
        // Ignore errors
      }
    };
    fetchStats();
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    // Validate file types
    const invalidFiles = acceptedFiles.filter(file => file.type !== 'application/pdf');
    if (invalidFiles.length > 0) {
      toast({
        title: t('aiInvoices.messages.invalidFiles'),
        description: t('aiInvoices.messages.onlyPdf'),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setIsUploading(true);
    setProcessingFiles(acceptedFiles.map(f => f.name));
    setUploadProgress(0);

    try {
      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];

        const formData = new FormData();
        formData.append('file', file);
        formData.append('invoice_type', invoiceType);

        // Upload and process file
        const response = await fetch(`${OpenAPI.BASE}/api/v1/ai-invoices/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${OpenAPI.TOKEN}`,
          },
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Upload failed');
        }

        setUploadProgress(((i + 1) / acceptedFiles.length) * 100);
      }

      toast({
        title: t('aiInvoices.messages.uploadSuccess'),
        description: t('aiInvoices.messages.filesProcessed', { count: acceptedFiles.length }),
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Refresh stats and extracted invoices
      queryClient.invalidateQueries({ queryKey: ['ai-invoices-stats'] });
      queryClient.invalidateQueries({ queryKey: ['extracted-invoices'] });

    } catch (error: any) {
      toast({
        title: t('aiInvoices.messages.uploadError'),
        description: error?.message || t('aiInvoices.messages.processingFailed'),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsUploading(false);
      setProcessingFiles([]);
      setUploadProgress(0);
    }
  }, [invoiceType, toast, queryClient, t]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: true,
    disabled: isUploading,
  });

  return (
    <Box maxW="4xl" mx="auto" p={6}>
      <VStack spacing={6} align="stretch">
        {/* Stats Cards */}
        {stats && stats.total > 0 && (
          <HStack spacing={4} wrap="wrap">
            <Card flex={1} minW="150px">
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold">
                  {stats.total}
                </Text>
                <Text color="gray.600">{t('aiInvoices.stats.total')}</Text>
              </CardBody>
            </Card>
            <Card flex={1} minW="150px">
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
                  {stats.pending_review}
                </Text>
                <Text color="gray.600">{t('aiInvoices.stats.pendingReview')}</Text>
              </CardBody>
            </Card>
            <Card flex={1} minW="150px">
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {stats.approved}
                </Text>
                <Text color="gray.600">{t('aiInvoices.stats.approved')}</Text>
              </CardBody>
            </Card>
            <Card flex={1} minW="150px">
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="red.500">
                  {stats.rejected}
                </Text>
                <Text color="gray.600">{t('aiInvoices.stats.rejected')}</Text>
              </CardBody>
            </Card>
          </HStack>
        )}

        {/* Upload Area */}
        <Card>
          <CardBody>
            <VStack spacing={4}>
              {/* Invoice Type Selection */}
              <FormControl>
                <FormLabel>{t('aiInvoices.invoiceType')}</FormLabel>
                <Select
                  value={invoiceType}
                  onChange={(e) => setInvoiceType(e.target.value as 'sales' | 'purchase')}
                  isDisabled={isUploading}
                >
                  <option value="purchase">{t('aiInvoices.types.purchase')}</option>
                  <option value="sales">{t('aiInvoices.types.sales')}</option>
                </Select>
              </FormControl>

              {/* Dropzone */}
              <Box
                {...getRootProps()}
                w="100%"
                border="2px dashed"
                borderColor={isDragActive ? 'blue.500' : 'gray.300'}
                borderRadius="lg"
                p={8}
                textAlign="center"
                cursor={isUploading ? 'not-allowed' : 'pointer'}
                bg={isDragActive ? 'blue.50' : 'gray.50'}
                transition="all 0.2s ease"
                _hover={!isUploading ? { borderColor: 'blue.400', bg: 'blue.50' } : {}}
              >
                <input {...getInputProps()} />

                {isUploading ? (
                  <VStack spacing={4}>
                    <Icon as={FiFile} boxSize={12} color="blue.500" />
                    <Text fontWeight="medium">{t('aiInvoices.processing')}</Text>
                    <Progress
                      value={uploadProgress}
                      size="sm"
                      colorScheme="blue"
                      w="100%"
                      hasStripe
                      isAnimated
                    />
                    {processingFiles.length > 0 && (
                      <VStack spacing={1} align="stretch" w="100%">
                        {processingFiles.map((filename, index) => (
                          <Text key={index} fontSize="sm" color="gray.600">
                            {index + 1}. {filename}
                          </Text>
                        ))}
                      </VStack>
                    )}
                  </VStack>
                ) : (
                  <VStack spacing={3}>
                    <Icon as={FiUpload} boxSize={12} color="gray.400" />
                    <Text fontSize="lg" fontWeight="medium">
                      {isDragActive
                        ? t('aiInvoices.dropHere')
                        : t('aiInvoices.dragAndDrop')
                      }
                    </Text>
                    <Text color="gray.600">
                      {t('aiInvoices.onlyPdfMax')}
                    </Text>
                  </VStack>
                )}
              </Box>
            </VStack>
          </CardBody>
        </Card>

        {/* Instructions */}
        <Alert status="info">
          <AlertIcon as={FiAlertCircle} />
          <Box>
            <AlertTitle>{t('aiInvoices.howItWorks')}</AlertTitle>
            <AlertDescription>
              <VStack align="start" spacing={1} mt={2}>
                <Text>• {t('aiInvoices.instructions.step1')}</Text>
                <Text>• {t('aiInvoices.instructions.step2')}</Text>
                <Text>• {t('aiInvoices.instructions.step3')}</Text>
                <Text>• {t('aiInvoices.instructions.step4')}</Text>
                <Text>• {t('aiInvoices.instructions.step5')}</Text>
              </VStack>
            </AlertDescription>
          </Box>
        </Alert>
      </VStack>
    </Box>
  );
};

export default InvoiceUpload;