import {
  Badge,
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { RecipesService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddRecipe from "../../components/Recipes/AddRecipe"
import { PaginationFooter } from "../../components/Common/PaginationFooter"

const recipesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/recipes")({
  component: Recipes,
  validateSearch: (search) => recipesSearchSchema.parse(search),
})

const PER_PAGE = 10

function getRecipesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      RecipesService.readRecipes({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["recipes", { page }],
  }
}

function RecipesTable() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: { [key: string]: string }) => ({ ...prev, page }) })

  const {
    data: recipes,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getRecipesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && recipes?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getRecipesQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>{t("recipes.code")}</Th>
              <Th>{t("recipes.name")}</Th>
              <Th>{t("recipes.outputQuantity")}</Th>
              <Th>{t("recipes.unit")}</Th>
              <Th>{t("recipes.version")}</Th>
              <Th>{t("recipes.status")}</Th>
              <Th>{t("recipes.productionCost")}</Th>
              <Th>{t("common.actions")}</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(8).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {recipes?.data.length === 0 ? (
                <Tr>
                  <Td colSpan={8}>
                    <Text textAlign="center" py={4} color="gray.500">
                      {t("recipes.messages.noRecipes")}
                    </Text>
                  </Td>
                </Tr>
              ) : (
                recipes?.data.map((recipe) => (
                  <Tr key={recipe.id} opacity={isPlaceholderData ? 0.5 : 1}>
                    <Td>
                      <Text fontWeight="medium">{recipe.code}</Text>
                    </Td>
                    <Td>
                      <Text>{recipe.name}</Text>
                    </Td>
                    <Td isNumeric>
                      <Text>{recipe.output_quantity}</Text>
                    </Td>
                    <Td>
                      <Text>{recipe.unit}</Text>
                    </Td>
                    <Td>
                      <Text color="gray.500">{recipe.version}</Text>
                    </Td>
                    <Td>
                      <Badge colorScheme={recipe.is_active ? "green" : "gray"}>
                        {recipe.is_active
                          ? t("statuses.active")
                          : t("statuses.inactive")}
                      </Badge>
                    </Td>
                    <Td isNumeric>
                      <Text>{recipe.production_cost}</Text>
                    </Td>
                    <Td>
                      <ActionsMenu type={"Recipe"} value={recipe} />
                    </Td>
                  </Tr>
                ))
              )}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  )
}

function Recipes() {
  const { t } = useTranslation()

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        {t("recipes.title")}
      </Heading>

      <Navbar type={"Recipe"} addModalAs={AddRecipe} />
      <RecipesTable />
    </Container>
  )
}
