import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import React from "react"
import { useForm } from "react-hook-form"

import {
  AccountsService,
  AssetsService,
  CustomersService,
  CustomerTypesService,
  ItemCategoriesService,
  ItemsService,
  ItemUnitsService,
  PurchasesService,
  SalesService,
  StoresService,
  SuppliersService,
  UsersService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface DeleteProps {
  type: string
  id: string
  isOpen: boolean
  onClose: () => void
}

const typeToQueryKey: Record<string, string> = {
  Item: "items",
  User: "users",
  Supplier: "suppliers",
  Category: "item-categories",
  Unit: "item-units",
  Type: "customer-types",
  Customer: "customers",
  Account: "accounts",
  Store: "stores",
  Purchase: "purchases",
  Sale: "sales",
  Asset: "assets",
}

const typeToLabel: Record<string, string> = {
  Item: "артикула",
  User: "потребителя",
  Supplier: "доставчика",
  Category: "категорията",
  Unit: "мерната единица",
  Type: "типа клиент",
  Customer: "клиента",
  Account: "сметката",
  Store: "склада",
  Purchase: "покупката",
  Sale: "продажбата",
  Asset: "актива",
}

const Delete = ({ type, id, isOpen, onClose }: DeleteProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const cancelRef = React.useRef<HTMLButtonElement | null>(null)
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteEntity = async (id: string) => {
    switch (type) {
      case "Item":
        await ItemsService.deleteItem({ id })
        break
      case "User":
        await UsersService.deleteUser({ userId: id })
        break
      case "Supplier":
        await SuppliersService.deleteSupplier({ id })
        break
      case "Category":
        await ItemCategoriesService.deleteItemCategory({ id })
        break
      case "Unit":
        await ItemUnitsService.deleteItemUnit({ id })
        break
      case "Type":
        await CustomerTypesService.deleteCustomerType({ id })
        break
      case "Customer":
        await CustomersService.deleteCustomer({ id })
        break
      case "Account":
        await AccountsService.deleteAccount({ id })
        break
      case "Store":
        await StoresService.deleteStore({ id })
        break
      case "Purchase":
        await PurchasesService.deletePurchase({ id })
        break
      case "Sale":
        await SalesService.deleteSale({ id })
        break
      case "Asset":
        await AssetsService.deleteAsset({ assetId: id })
        break
      default:
        throw new Error(`Unexpected type: ${type}`)
    }
  }

  const mutation = useMutation({
    mutationFn: deleteEntity,
    onSuccess: () => {
      showToast(
        "Успех",
        `${typeToLabel[type] || type} беше изтрит(а) успешно.`,
        "success",
      )
      onClose()
    },
    onError: () => {
      showToast(
        "Грешка",
        `Възникна грешка при изтриването на ${typeToLabel[type] || type}.`,
        "error",
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: [typeToQueryKey[type] || type.toLowerCase() + "s"],
      })
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <>
      <AlertDialog
        isOpen={isOpen}
        onClose={onClose}
        leastDestructiveRef={cancelRef}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <AlertDialogOverlay>
          <AlertDialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
            <AlertDialogHeader>Изтриване</AlertDialogHeader>

            <AlertDialogBody>
              {type === "User" && (
                <span>
                  Всички елементи, свързани с този потребител, също ще бъдат{" "}
                  <strong>окончателно изтрити. </strong>
                </span>
              )}
              Сигурни ли сте? Това действие не може да бъде отменено.
            </AlertDialogBody>

            <AlertDialogFooter gap={3}>
              <Button variant="danger" type="submit" isLoading={isSubmitting}>
                Изтрий
              </Button>
              <Button
                ref={cancelRef}
                onClick={onClose}
                isDisabled={isSubmitting}
              >
                Отказ
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}

export default Delete
