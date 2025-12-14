import {
  Button,
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Icon,
  Input,
  Menu,
  MenuButton,
  MenuDivider,
  MenuItem,
  MenuList,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Spinner,
  Text,
  useColorModeValue,
  useDisclosure,
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
  const [errors, setErrors] = useState<{ name?: string }>({})

  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.600")
  const hoverBg = useColorModeValue("gray.100", "gray.700")
  const activeBg = useColorModeValue("blue.50", "blue.900")

  const handleSubmitNewOrg = () => {
    const newErrors: { name?: string } = {}

    if (!newOrgName.trim()) {
      newErrors.name = t("errors.requiredField")
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    create({
      name: newOrgName.trim(),
    })

    setNewOrgName("")
    setErrors({})
    onClose()
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
            <FormControl isInvalid={!!errors.name}>
              <FormLabel>{t("organizations.name")}</FormLabel>
              <Input
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder={t("organizations.namePlaceholder")}
              />
              <FormErrorMessage>{errors.name}</FormErrorMessage>
            </FormControl>
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
