import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { AccountPublic, AssetPublic, UserPublic, StorePublic } from "../../client"
import EditUser from "../Admin/EditUser"
import EditAccount from "../Accounts/EditAccount"
import EditStore from "../Stores/EditStore"
import EditAsset from "../Assets/EditAsset"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: UserPublic | AccountPublic | StorePublic | AssetPublic
  disabled?: boolean
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()
  const componentMap = {
    User: (
      <EditUser
        user={value as UserPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Account: (
      <EditAccount
        account={value as AccountPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Store: (
      <EditStore
        store={value as StorePublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
    Asset: (
      <EditAsset
        asset={value as AssetPublic}
        isOpen={editUserModal.isOpen}
        onClose={editUserModal.onClose}
      />
    ),
  } as const;

  type ComponentKey = keyof typeof componentMap;

  function isValidComponentKey(key: string): key is ComponentKey {
    return key in componentMap;
  }


  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          <MenuItem
            onClick={editUserModal.onOpen}
            icon={<FiEdit fontSize="16px" />}
          >
            Edit {type}
          </MenuItem>
          <MenuItem
            onClick={deleteModal.onOpen}
            icon={<FiTrash fontSize="16px" />}
            color="ui.danger"
          >
            Delete {type}
          </MenuItem>
        </MenuList>
        {isValidComponentKey(type) ? componentMap[type] : null}
        <Delete
          type={type}
          id={value.id}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  )
}

export default ActionsMenu
