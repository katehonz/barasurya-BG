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
  StoresService,
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
  User: "users",
  Account: "accounts",
  Store: "stores",
  Asset: "assets",
}

const typeToLabel: Record<string, string> = {
  User: "потребителя",
  Account: "сметката",
  Store: "склада",
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
      case "User":
        await UsersService.deleteUser({ userId: id })
        break
      case "Account":
        await AccountsService.deleteAccount({ id })
        break
      case "Store":
        await StoresService.deleteStore({ id })
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
