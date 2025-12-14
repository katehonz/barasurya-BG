import {
  Button,
  Flex,
  Icon,
  Menu,
  MenuButton,
  MenuDivider,
  MenuItem,
  MenuList,
  Spinner,
  Text,
  useColorModeValue,
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
  FormErrorMessage,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiBriefcase, FiCheck, FiChevronDown, FiPlus } from "react-icons/fi"

import useOrganization from "../../hooks/useOrganization"

const OrganizationSwitcher = () => {
  const { t } = useTranslation()
  const {
    organizations,
    currentOrganization,
    isLoadingOrganizations,
    isSwitching,
    isCreating,
    switchTo,
    create,
    hasOrganizations,
  } = useOrganization()

  const { isOpen, onOpen, onClose } = useDisclosure()
  const [newOrgName, setNewOrgName] = useState("")
  const [newOrgSlug, setNewOrgSlug] = useState("")
  const [errors, setErrors] = useState<{ name?: string; slug?: string }>({})

  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.600")
  const hoverBg = useColorModeValue("gray.100", "gray.700")
  const activeBg = useColorModeValue("blue.50", "blue.900")

  const handleSubmitNewOrg = () => {
    const newErrors: { name?: string; slug?: string } = {}

    if (!newOrgName.trim()) {
      newErrors.name = t("errors.requiredField")
    }
    if (!newOrgSlug.trim()) {
      newErrors.slug = t("errors.requiredField")
    } else if (!/^[a-z0-9-]+$/.test(newOrgSlug)) {
      newErrors.slug = t("organizations.slugFormat")
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    create({
      name: newOrgName.trim(),
      slug: newOrgSlug.trim().toLowerCase(),
    })

    setNewOrgName("")
    setNewOrgSlug("")
    setErrors({})
    onClose()
  }

  const handleNameChange = (value: string) => {
    setNewOrgName(value)
    // Auto-generate slug from name
    const slug = value
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
    setNewOrgSlug(slug)
  }

  if (isLoadingOrganizations) {
    return (
      <Flex align="center" p={2}>
        <Spinner size="sm" mr={2} />
        <Text fontSize="sm">{t("common.loading")}</Text>
      </Flex>
    )
  }

  return (
    <>
      <Menu>
        <MenuButton
          as={Button}
          variant="ghost"
          size="sm"
          w="full"
          justifyContent="space-between"
          rightIcon={<FiChevronDown />}
          leftIcon={<FiBriefcase />}
          isLoading={isSwitching}
          borderWidth={1}
          borderColor={borderColor}
          bg={bgColor}
          _hover={{ bg: hoverBg }}
          px={3}
          py={2}
        >
          <Text
            flex={1}
            textAlign="left"
            noOfLines={1}
            fontSize="sm"
            fontWeight="medium"
          >
            {currentOrganization?.name || t("organizations.selectOrganization")}
          </Text>
        </MenuButton>
        <MenuList
          bg={bgColor}
          borderColor={borderColor}
          shadow="lg"
          zIndex={10}
          minW="200px"
        >
          {organizations.map((org) => (
            <MenuItem
              key={org.id}
              onClick={() => switchTo(org.id)}
              bg={org.id === currentOrganization?.id ? activeBg : "transparent"}
              _hover={{ bg: hoverBg }}
            >
              <Flex align="center" justify="space-between" w="full">
                <Flex align="center">
                  <Icon as={FiBriefcase} mr={2} />
                  <Text fontSize="sm">{org.name}</Text>
                </Flex>
                {org.id === currentOrganization?.id && (
                  <Icon as={FiCheck} color="green.500" />
                )}
              </Flex>
            </MenuItem>
          ))}

          {hasOrganizations && <MenuDivider />}

          <MenuItem
            onClick={onOpen}
            icon={<FiPlus />}
            _hover={{ bg: hoverBg }}
          >
            <Text fontSize="sm" fontWeight="medium">
              {t("organizations.createNew")}
            </Text>
          </MenuItem>
        </MenuList>
      </Menu>

      {/* Create Organization Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("organizations.createOrganization")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isInvalid={!!errors.name}>
                <FormLabel>{t("organizations.name")}</FormLabel>
                <Input
                  value={newOrgName}
                  onChange={(e) => handleNameChange(e.target.value)}
                  placeholder={t("organizations.namePlaceholder")}
                />
                <FormErrorMessage>{errors.name}</FormErrorMessage>
              </FormControl>

              <FormControl isInvalid={!!errors.slug}>
                <FormLabel>{t("organizations.slug")}</FormLabel>
                <Input
                  value={newOrgSlug}
                  onChange={(e) => setNewOrgSlug(e.target.value.toLowerCase())}
                  placeholder={t("organizations.slugPlaceholder")}
                />
                <FormErrorMessage>{errors.slug}</FormErrorMessage>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {t("organizations.slugHelp")}
                </Text>
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t("common.cancel")}
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleSubmitNewOrg}
              isLoading={isCreating}
            >
              {t("common.create")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default OrganizationSwitcher
