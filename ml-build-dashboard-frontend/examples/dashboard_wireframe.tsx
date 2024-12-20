import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const BuildDashboard = () => {
  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Build Dashboard</h1>
        <div className="flex gap-4 mb-4">
          <Card className="w-1/4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Queue Time</CardTitle>
              <span className="text-gray-500 text-sm">⏱️</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">45m</div>
              <p className="text-xs text-muted-foreground">Average wait time</p>
            </CardContent>
          </Card>
          <Card className="w-1/4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Build Status</CardTitle>
              <span className="text-gray-500 text-sm">📊</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">85%</div>
              <p className="text-xs text-muted-foreground">Success rate</p>
            </CardContent>
          </Card>
          <Card className="w-1/4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Force Merges</CardTitle>
              <span className="text-gray-500 text-sm">🔄</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">Last 24 hours</p>
            </CardContent>
          </Card>
          <Card className="w-1/4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
              <span className="text-gray-500 text-sm">⚠️</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2</div>
              <p className="text-xs text-muted-foreground">Require attention</p>
            </CardContent>
          </Card>
        </div>
      </div>

      <Tabs defaultValue="waterfall" className="w-full">
        <TabsList>
          <TabsTrigger value="waterfall">Waterfall View</TabsTrigger>
          <TabsTrigger value="triage">Triage</TabsTrigger>
          <TabsTrigger value="developer">Developer View</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>
        <TabsContent value="waterfall" className="bg-white p-4 rounded-lg">
          <div className="h-96 border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Build Waterfall View</p>
          </div>
        </TabsContent>
        <TabsContent value="triage" className="bg-white p-4 rounded-lg">
          <div className="h-96 border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Build Triage View</p>
          </div>
        </TabsContent>
        <TabsContent value="developer" className="bg-white p-4 rounded-lg">
          <div className="h-96 border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Developer Build View</p>
          </div>
        </TabsContent>
        <TabsContent value="alerts" className="bg-white p-4 rounded-lg">
          <div className="h-96 border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Build Alerts View</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BuildDashboard;
