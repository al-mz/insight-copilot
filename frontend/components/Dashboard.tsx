"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { AreaChart } from "./ui/area-chart";
import { BarChart } from "./ui/bar-chart";
import { DonutChart } from "./ui/pie-chart";
import { SearchResults } from "./generative-ui/SearchResults";
import { useEffect, useState } from "react";

interface SalesData {
  date: string;
  Sales: number;
  Profit: number;
  Expenses: number;
  Customers: number;
  [key: string]: string | number;
}

interface ProductData {
  title: string;
  rental_count: number;
  rental_rate: number;
  total_revenue: number;
  [key: string]: string | number;
}

interface CategoryData {
  category: string;
  film_count: number;
  avg_rental_rate: number;
  total_revenue: number;
  [key: string]: string | number;
}

interface RegionalData {
  region: string;
  sales: number;
  marketShare: number;
  [key: string]: string | number;
}

interface CustomerData {
  customer_name: string;
  rental_count: number;
  total_spent: number;
  [key: string]: string | number;
}

export function Dashboard() {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [productData, setProductData] = useState<ProductData[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryData[]>([]);
  const [regionalData, setRegionalData] = useState<RegionalData[]>([]);
  const [customerData, setCustomerData] = useState<CustomerData[]>([]);
  const [metrics, setMetrics] = useState({
    totalRevenue: 0,
    totalProfit: 0,
    totalCustomers: 0,
    conversionRate: "0%",
    averageOrderValue: "0",
    profitMargin: "0%"
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch sales overview data
        const salesResponse = await fetch('http://0.0.0.0:8000/api/v1/insights/sales-overview');
        const salesResult = await salesResponse.json();
        if (salesResult.status === 'success') {
          setSalesData(salesResult.data);
          // Calculate metrics
          const totalRevenue = salesResult.data.reduce((sum: number, item: SalesData) => sum + item.Sales, 0);
          const totalProfit = salesResult.data.reduce((sum: number, item: SalesData) => sum + item.Profit, 0);
          const totalCustomers = salesResult.data.reduce((sum: number, item: SalesData) => sum + item.Customers, 0);
          const avgOrderValue = (totalRevenue / totalCustomers).toFixed(2);
          const profitMargin = ((totalProfit / totalRevenue) * 100).toFixed(1);

          setMetrics({
            totalRevenue,
            totalProfit,
            totalCustomers,
            conversionRate: "12.3%", // This would need a separate calculation
            averageOrderValue: avgOrderValue,
            profitMargin: profitMargin + "%"
          });
        }

        // Fetch top films data
        const filmsResponse = await fetch('http://0.0.0.0:8000/api/v1/insights/top-films');
        const filmsResult = await filmsResponse.json();
        if (filmsResult.status === 'success') {
          setProductData(filmsResult.data);
        }

        // Fetch category performance data
        const categoryResponse = await fetch('http://0.0.0.0:8000/api/v1/insights/category-performance');
        const categoryResult = await categoryResponse.json();
        if (categoryResult.status === 'success') {
          setCategoryData(categoryResult.data);
        }

        // Fetch regional sales data
        const regionalResponse = await fetch('http://0.0.0.0:8000/api/v1/insights/regional-sales');
        const regionalResult = await regionalResponse.json();
        if (regionalResult.status === 'success') {
          setRegionalData(regionalResult.data);
        }

        // Fetch customer activity data
        const customerResponse = await fetch('http://0.0.0.0:8000/api/v1/insights/customer-activity');
        const customerResult = await customerResponse.json();
        if (customerResult.status === 'success') {
          setCustomerData(customerResult.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, []);

  // Make data available to the Copilot
  useCopilotReadable({
    description: "Dashboard data including sales trends, product performance, and category distribution",
    value: {
      salesData,
      productData,
      categoryData,
      regionalData,
      customerData,
      metrics
    }
  });

  // Define render only search action
  useCopilotAction({
    name: "searchInternet",
    available: "disabled",
    description: "Searches the internet for information.",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "The query to search the internet for.",
        required: true,
      }
    ],
    render: ({args, status}) => {
      return <SearchResults query={args.query || 'No query provided'} status={status} />;
    }
  });

  // Color palettes for different charts
  const colors = {
    salesOverview: ["#3b82f6", "#10b981", "#ef4444"],  // Blue, Green, Red
    productPerformance: ["#8b5cf6", "#6366f1", "#4f46e5"],  // Purple spectrum
    categories: ["#3b82f6", "#64748b", "#10b981", "#f59e0b", "#94a3b8"],  // Mixed
    regional: ["#059669", "#10b981", "#34d399", "#6ee7b7", "#a7f3d0"],  // Green spectrum
    demographics: ["#f97316", "#f59e0b", "#eab308", "#facc15", "#fde047"]  // Orange to Yellow
  };

  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4 w-full">
      {/* Key Metrics */}
      <div className="col-span-1 md:col-span-2 lg:col-span-4">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Total Revenue</p>
            <p className="text-xl font-semibold text-gray-900">${metrics.totalRevenue.toLocaleString()}</p>
          </div>
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Total Profit</p>
            <p className="text-xl font-semibold text-gray-900">${metrics.totalProfit.toLocaleString()}</p>
          </div>
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Customers</p>
            <p className="text-xl font-semibold text-gray-900">{metrics.totalCustomers.toLocaleString()}</p>
          </div>
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Conversion Rate</p>
            <p className="text-xl font-semibold text-gray-900">{metrics.conversionRate}</p>
          </div>
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Avg Order Value</p>
            <p className="text-xl font-semibold text-gray-900">${metrics.averageOrderValue}</p>
          </div>
          <div className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
            <p className="text-xs text-gray-500">Profit Margin</p>
            <p className="text-xl font-semibold text-gray-900">{metrics.profitMargin}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <Card className="col-span-1 md:col-span-2 lg:col-span-4">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Sales Overview</CardTitle>
          <CardDescription className="text-xs">Monthly sales and profit data</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            <AreaChart
              data={salesData}
              index="date"
              categories={["Sales", "Profit", "Expenses"]}
              colors={colors.salesOverview}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={true}
              showGrid={true}
              showXAxis={true}
              showYAxis={true}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Top Films</CardTitle>
          <CardDescription className="text-xs">Most rented films</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            <BarChart
              data={productData}
              index="title"
              categories={["total_revenue"]}
              colors={colors.productPerformance}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGrid={true}
              layout="horizontal"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Category Performance</CardTitle>
          <CardDescription className="text-xs">Revenue by film category</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            <DonutChart
              data={categoryData}
              category="total_revenue"
              index="category"
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              colors={colors.categories}
              centerText="Categories"
              paddingAngle={0}
              showLabel={false}
              showLegend={true}
              innerRadius={45}
              outerRadius="90%"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Regional Sales</CardTitle>
          <CardDescription className="text-xs">Sales by country</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            <BarChart
              data={regionalData}
              index="region"
              categories={["sales"]}
              colors={colors.regional}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGrid={true}
              layout="horizontal"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1 md:col-span-1 lg:col-span-2">
        <CardHeader className="pb-1 pt-3">
          <CardTitle className="text-base font-medium">Top Customers</CardTitle>
          <CardDescription className="text-xs">Highest spending customers</CardDescription>
        </CardHeader>
        <CardContent className="p-3">
          <div className="h-60">
            <BarChart
              data={customerData}
              index="customer_name"
              categories={["total_spent"]}
              colors={colors.demographics}
              valueFormatter={(value) => `$${value.toLocaleString()}`}
              showLegend={false}
              showGrid={true}
              layout="horizontal"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
